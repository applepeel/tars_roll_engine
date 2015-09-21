import re

from django.db import IntegrityError, transaction
from django.utils.deconstruct import deconstructible

from roll_engine.constants import PENDING
from roll_engine.exceptions import BatchPatternError


@deconstructible
class BatchFactory(object):
    def __init__(self, max_percentage=25, delimiter='+'):
        self.max_percentage = max_percentage
        self.delimiter = delimiter

    def _parse_batch_pattern(self, batch_pattern):
        raw_percents = batch_pattern.split(self.delimiter)
        return [int(p.strip('%')) for p in raw_percents]

    def preview_slice(self, batch_pattern, servers, forts):
        percentages = self._parse_batch_pattern(batch_pattern)
        return self.slice_servers(percentages, servers, forts)

    def slice_servers(self, percentages, servers, forts):
        fort_servers = [svr for svr in servers if svr['hostname'] in forts]
        normal_servers = [svr for svr in servers
                          if svr['hostname'] not in forts]
        servers_count = rest_count = len(normal_servers)
        slice_counts = []

        while rest_count > 0:
            percentage = (self.max_percentage
                          if not percentages else percentages.pop(0))
            count = min(int(percentage*servers_count / 100.0), rest_count) or 1
            slice_counts.append(count)
            rest_count -= count

        # collect (start, stop) indices for every slice
        slice_indices = reduce(lambda x, y: x + [x[-1] + y], slice_counts, [0])

        sliced_servers = [normal_servers[i:j]
                          for i, j in zip(slice_indices, slice_indices[1:])]
        if fort_servers:
            sliced_servers.insert(0, fort_servers)
        return sliced_servers

    def validate_batch_pattern(self, pattern_str):
        try:
            if re.match(r'^\d+%$', pattern_str):
                percentage = int(pattern_str.strip('%'))
                if not 0 < percentage <= self.max_percentage:
                    raise BatchPatternError(
                        'percentage should be a value located in (0, {0}]%'
                        .format(self.max_percentage))
                percentages = [percentage for _ in range(100/percentage)]
                if 100 % percentage:
                    percentages.append(100 % percentage)
            else:
                # TODO: Move this to VarialBatchFactory
                # verify input pattern_str:
                # 1. format follow convention
                # 2. sum of all percentages equal to 100%
                matched = re.match(r'^\d+%(?:\+\d+%){1,99}$', pattern_str)
                if matched:
                    prog = re.compile(r'(\d+)%')
                    percentages = re.findall(prog, pattern_str)
                    percentages = [int(i) for i in percentages]
                    if 100 != int(sum(percentages)):
                        raise BatchPatternError(
                            'sum of percentages is not equal to 100%')
                else:
                    raise BatchPatternError('illegal pattern')
        except (ValueError, BatchPatternError) as e:
            raise BatchPatternError(e)
        return self.delimiter.join(['{0}%'.format(p) for p in percentages])

    def generate_deployment_batches(self, deployment, servers, forts=None):
        if forts is None:
            forts = []

        percentages = self._parse_batch_pattern(deployment.config.batch_pattern)
        sliced_targets = self.slice_servers(percentages, servers, forts)

        try:
            with transaction.atomic():
                batch_model = deployment.batches.model
                for idx, tgts in enumerate(sliced_targets, 1):
                    batch = batch_model.objects.create(
                        deployment=deployment, index=idx)
                    self.generate_deployment_targets(batch, tgts)
        except IntegrityError as e:
            raise IntegrityError('Generate batches and targets error: {0}'
                                 .format(e))

    def generate_deployment_targets(self, deployment_batch, batch_servers):
        kwargs = dict(batch=deployment_batch, status=PENDING)
        if deployment_batch.is_fort_batch():
            kwargs.update(is_fort=True)
        target_model = deployment_batch.targets.model
        target_model.objects.bulk_create(target_model(hostname=svr['hostname'],
                                                      **kwargs)
                                         for svr in batch_servers)

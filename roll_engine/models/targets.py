from django.db import models

from roll_engine.exceptions import MetaMissing, DeploymentError
from roll_engine.utils.log import get_logger
from roll_engine.mixins import TargetMixin

from .base import FSMedModel, InheritanceMetaclass


re_logger = get_logger()


class DeploymentTarget(TargetMixin, FSMedModel):
    __metaclass__ = InheritanceMetaclass

    task_id = models.CharField(max_length=36, null=True, blank=True)
    is_fort = models.BooleanField(default=False)
    hostname = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True
        salt_timeout = 180

    @classmethod
    def validate_meta(cls):
        if 'salt_timeout' not in dir(cls._meta):
            raise MetaMissing('missing salt_timeout in Meta of {} Model'.
                              format(cls.__name__))

    def get_object(self):
        return self

    def __unicode__(self):
        return self.hostname

    def get_extras(self):
        return {'deploy': self.batch.deployment, 'tgt': self}

    def pull_out(self):
        raise DeploymentError('override pull_out to implement disable from LB, '
                              'return boolean to indicate result')

    def pull_in(self):
        raise DeploymentError('override pull_in to implement enable in LB, '
                              'return boolean to indicate result')

    def call_salt(self, cmd, *args, **kwargs):
        hostname = self.hostname
        deployment = self.batch.deployment
        salt_client, salt_module = deployment.salt_client_and_module()
        module_func = '{module}.{cmd}'.format(module=salt_module, cmd=cmd)
        log_extra = deployment.build_deployment_log(self)
        kwargs.update({'log_extra': log_extra})
        kwargs.setdefault('wait_timeout', self._meta.salt_timeout)

        try:
            resp, description = salt_client.run_module_await(
                hostname, module_func, *args, **kwargs)
        except Exception as e:
            resp = {}
            description = 'salt error: {}'.format(e)
        description = description or 'view agent log for detail'

        if hostname in resp:
            if isinstance(resp[hostname], basestring):
                return True, resp[hostname]
            elif resp[hostname]:
                return True, description
        return False, description

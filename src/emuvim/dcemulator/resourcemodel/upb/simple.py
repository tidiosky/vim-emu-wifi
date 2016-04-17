"""
Playground for resource models created by University of Paderborn.
"""
import time
import json
import logging
from emuvim.dcemulator.resourcemodel import BaseResourceModel

LOG = logging.getLogger("rm.upb.simple")
LOG.setLevel(logging.DEBUG)


class UpbSimpleCloudDcRM(BaseResourceModel):
    """
    This will be an example resource model that limits the overall
    resources that can be deployed per data center.
    No over provisioning. Resources are fixed throughout entire container
    lifetime.
    """

    def __init__(self, max_cu=32, max_mu=1024,
                 deactivate_cpu_limit=False,
                 deactivate_mem_limit=False):
        """
        Initialize model.
        :param max_cu: Maximum number of compute units available in this DC.
        :param max_mu: Maximum memory of entire dc.
        :return:
        """
        self.dc_max_cu = max_cu
        self.dc_max_mu = max_mu
        self.dc_alloc_cu = 0
        self.dc_alloc_mu = 0
        self.deactivate_cpu_limit = deactivate_cpu_limit
        self.deactivate_mem_limit = deactivate_mem_limit
        super(self.__class__, self).__init__()

    def allocate(self, d):
        """
        Allocate resources for the given container.
        Defined by d.flavor_name
        :param d: container
        :return:
        """
        self._allocated_compute_instances[d.name] = d
        if not self.deactivate_cpu_limit:
            self._allocate_cpu(d)
        if not self.deactivate_mem_limit:
            self._allocate_mem(d)
        self._apply_limits()

    def _allocate_cpu(self, d):
        """
        Actually allocate (bookkeeping)
        :param d: container
        :return:
        """
        fl_cu = self._get_flavor(d).get("compute")
        # check for over provisioning
        if self.dc_alloc_cu + fl_cu > self.dc_max_cu:
            raise Exception("Not enough compute resources left.")
        self.dc_alloc_cu += fl_cu

    def _allocate_mem(self, d):
        """
        Actually allocate (bookkeeping)
        :param d: container
        :return:
        """
        fl_mu = self._get_flavor(d).get("memory")
        # check for over provisioning
        if self.dc_alloc_mu + fl_mu > self.dc_max_mu:
            raise Exception("Not enough memory resources left.")
        self.dc_alloc_mu += fl_mu

    def free(self, d):
        """
        Free resources allocated to the given container.
        :param d: container
        :return:
        """
        del self._allocated_compute_instances[d.name]
        if not self.deactivate_cpu_limit:
            self._free_cpu(d)
        if not self.deactivate_mem_limit:
            self._free_mem(d)
        self._apply_limits()

    def _free_cpu(self, d):
        """
        Free resources.
        :param d: container
        :return:
        """
        self.dc_alloc_cu -= self._get_flavor(d).get("compute")

    def _free_mem(self, d):
        """
        Free resources.
        :param d: container
        :return:
        """
        self.dc_alloc_mu -= self._get_flavor(d).get("memory")

    def _apply_limits(self):
        """
        Recalculate real resource limits for all allocated containers and apply them
        to their cgroups.
        We have to recalculate for all to allow e.g. overprovisioning models.
        :return:
        """
        for d in self._allocated_compute_instances.itervalues():
            if not self.deactivate_cpu_limit:
                self._apply_cpu_limits(d)
            if not self.deactivate_mem_limit:
                self._apply_mem_limits(d)

    def _apply_cpu_limits(self, d):
        """
        Calculate real CPU limit (CFS bandwidth) and apply.
        :param d: container
        :return:
        """
        number_cu = self._get_flavor(d).get("compute")
        # get cpu time fraction for entire emulation
        e_cpu = self.registrar.e_cpu
        # calculate cpu time fraction of a single compute unit
        single_cu = float(e_cpu) / sum([rm.dc_max_cu for rm in list(self.registrar.resource_models)])
        # calculate cpu time fraction for container with given flavor
        cpu_time_percentage = single_cu * number_cu
        # calculate cpu period and quota for CFS
        # (see: https://www.kernel.org/doc/Documentation/scheduler/sched-bwc.txt)
        # Attention minimum cpu_quota is 1ms (micro)
        cpu_period = 1000000  # lets consider a fixed period of 1000000 microseconds for now
        cpu_quota = cpu_period * cpu_time_percentage  # calculate the fraction of cpu time for this container
        # ATTENTION >= 1000 to avoid a invalid argument system error ... no idea why
        if cpu_quota < 1000:
            cpu_quota = 1000
            LOG.warning("Increased CPU quota for %r to avoid system error." % d.name)
        # apply to container if changed
        if d.cpu_period != cpu_period or d.cpu_quota != cpu_quota:
            LOG.debug("Setting CPU limit for %r: cpu_quota = cpu_period * limit = %f * %f = %f" % (
                      d.name, cpu_period, cpu_time_percentage, cpu_quota))
            d.updateCpuLimit(cpu_period=int(cpu_period), cpu_quota=int(cpu_quota))

    def _apply_mem_limits(self, d):
        """
        Calculate real mem limit and apply.
        :param d: container
        :return:
        """
        number_mu = self._get_flavor(d).get("memory")
        # get memory amount for entire emulation
        e_mem = self.registrar.e_mem
        # calculate amount of memory for a single mu
        single_mu = float(e_mem) / sum([rm.dc_max_mu for rm in list(self.registrar.resource_models)])
        # calculate mem for given flavor
        mem_limit = single_mu * number_mu
        # ATTENTION minimum mem_limit per container is 4MB
        if mem_limit < 4:
            mem_limit = 4
            LOG.warning("Increased MEM limit for %r because it was less than 4.0 MB." % d.name)
        # to byte!
        mem_limit = int(mem_limit*1024*1024)
        # apply to container if changed
        if d.mem_limit != mem_limit:
            LOG.debug("Setting MEM limit for %r: mem_limit = %f MB" % (d.name, mem_limit/1024/1024))
            d.updateMemoryLimit(mem_limit=mem_limit)

    def get_state_dict(self):
        """
        Return the state of the resource model as simple dict.
        Helper method for logging functionality.
        :return:
        """
        # collect info about all allocated instances
        allocation_state = dict()
        for k, d in self._allocated_compute_instances.iteritems():
            s = dict()
            s["cpu_period"] = d.cpu_period
            s["cpu_quota"] = d.cpu_quota
            s["cpu_shares"] = d.cpu_shares
            s["mem_limit"] = d.mem_limit
            s["memswap_limit"] = d.memswap_limit
            allocation_state[k] = s
        # final result
        r = dict()
        r["e_cpu"] = self.registrar.e_cpu
        r["e_mem"] = self.registrar.e_mem
        r["dc_max_cu"] = self.dc_max_cu
        r["dc_max_mu"] = self.dc_max_mu
        r["dc_alloc_cu"] = self.dc_alloc_cu
        r["dc_alloc_mu"] = self.dc_alloc_mu
        r["allocation_state"] = allocation_state
        return r

    def _get_flavor(self, d):
        """
        Get flavor assigned to given container.
        Identified by d.flavor_name.
        :param d: container
        :return:
        """
        if d.flavor_name not in self._flavors:
            raise Exception("Flavor %r does not exist" % d.flavor_name)
        return self._flavors.get(d.flavor_name)

    def _write_log(self, d, path, action):
        """
        Helper to log RM info for experiments.
        :param d: container
        :param path: log path
        :param action: allocate or free
        :return:
        """
        if path is None:
            return
        # we have a path: write out RM info
        l = dict()
        l["t"] = time.time()
        l["container_state"] = d.getStatus()
        l["action"] = action
        l["rm_state"] = self.get_state_dict()
        # append to logfile
        with open(path, "a") as f:
            f.write("%s\n" % json.dumps(l))
"""Dagster Job assembly for Tinnery Flow invocations.

Tinnery Flow 调用到 Dagster Job 的组装。
"""

from dagster import job


def make_flow_job(flow_op, name: str | None = None):
    """Build a single-op Dagster job around a Flow op from make_flow_op.

    围绕 make_flow_op 生成的 Flow op 构建单 op 的 Dagster job。

    Args:
        flow_op: A Dagster op created by tinnery.dagster.make_flow_op
                 由 tinnery.dagster.make_flow_op 创建的 Dagster op
        name: Optional job name (defaults to ``<op_name>_job``)
              可选 job 名称（默认为 ``<op_name>_job``）

    Returns:
        A Dagster job executing the Flow op
        执行该 Flow op 的 Dagster job
    """
    job_name = name or f"{flow_op.name}_job"

    @job(name=job_name)
    def _flow_job():
        flow_op()

    return _flow_job

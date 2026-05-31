from nodus_state import AgentStatus, EnvelopeStatus, FlowStatus, UnitStatus, UnitType, WaitType


def test_flow_status_constants():
    assert FlowStatus.RUNNING == "running"
    assert FlowStatus.WAITING == "waiting"
    assert FlowStatus.COMPLETED in FlowStatus.TERMINAL
    assert FlowStatus.FAILED in FlowStatus.TERMINAL
    assert FlowStatus.RUNNING in FlowStatus.ALL
    assert len(FlowStatus.ALL) == 5


def test_unit_status_constants():
    assert UnitStatus.PENDING == "pending"
    assert UnitStatus.WAITING == "waiting"
    assert UnitStatus.RESUMED == "resumed"
    assert UnitStatus.COMPLETED in UnitStatus.TERMINAL
    assert UnitStatus.FAILED in UnitStatus.TERMINAL
    assert len(UnitStatus.ALL) == 6


def test_agent_status_constants():
    assert AgentStatus.PENDING_APPROVAL == "pending_approval"
    assert AgentStatus.APPROVED == "approved"
    assert AgentStatus.COMPLETED in AgentStatus.TERMINAL
    assert AgentStatus.EXECUTING in AgentStatus.ACTIVE
    assert len(AgentStatus.ALL) == 5


def test_unit_type_constants():
    assert UnitType.FLOW == "flow"
    assert UnitType.AGENT == "agent"
    assert UnitType.OPERATION == "operation"
    assert UnitType.JOB == "job"
    assert len(UnitType.ALL) == 4


def test_wait_type_constants():
    assert WaitType.EVENT == "event"
    assert WaitType.TIME == "time"
    assert WaitType.EXTERNAL == "external"
    assert len(WaitType.ALL) == 3


def test_envelope_status_constants():
    assert EnvelopeStatus.SUCCESS == "SUCCESS"
    assert EnvelopeStatus.ERROR == "ERROR"
    assert EnvelopeStatus.WAITING == "WAITING"


def test_terminal_disjoint_from_active():
    for t in FlowStatus.TERMINAL:
        assert t not in FlowStatus.ACTIVE
    for t in UnitStatus.TERMINAL:
        assert t not in UnitStatus.ACTIVE
    for t in AgentStatus.TERMINAL:
        assert t not in AgentStatus.ACTIVE

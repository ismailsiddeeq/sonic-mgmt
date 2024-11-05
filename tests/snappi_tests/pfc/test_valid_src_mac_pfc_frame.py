import logging
import pytest


from tests.snappi_tests.pfc.files.valid_src_mac_pfc_frame_helper import run_pfc_valid_src_mac_test
from tests.common.helpers.assertions import pytest_require
from tests.common.fixtures.conn_graph_facts import conn_graph_facts,\
    fanout_graph_facts # noqa F401
from tests.common.snappi_tests.snappi_fixtures import snappi_api_serv_ip, snappi_api_serv_port,\
    snappi_api, snappi_testbed_config, is_snappi_multidut # noqa F401
from tests.common.snappi_tests.qos_fixtures import prio_dscp_map, all_prio_list, lossless_prio_list,\
    lossy_prio_list # noqa F401
from tests.common.snappi_tests.snappi_test_params import SnappiTestParams
from tests.common.snappi_tests.common_helpers import packet_capture
from tests.common.cisco_data import is_cisco_device

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.topology('tgen')]


def test_valid_pfc_frame_src_mac(
                    snappi_api, # noqa F811
                    snappi_testbed_config, # noqa F811
                    conn_graph_facts, # noqa F811
                    fanout_graph_facts, # noqa F811
                    duthosts,
                    rand_one_dut_hostname,
                    rand_one_dut_portname_oper_up,
                    lossless_prio_list, # noqa F811
                    prio_dscp_map): # noqa F811
    """
    Test if PFC Pause frame generated by device under test (DUT) is having a valid src mac

    Topology:
    snappi (1) -> DUT -> snappi (2)

    Test steps:
    1) Create congestion on ingress port of ixia (snappi 2). This is done by letting 1 send data traffic to 2, and 2
        sending PFC pause frames to DUT.
    2) tgen 2 sends PFC pause frames to DUT.
    3) DUT responds to PFC frames by also sending back PFC pause frames back to tgen 1.
    4) Using packet capture on tgen 1 port, verify PFC pause frames meet IEEE 802.1Qbb code point standards.
        a) There is a pause quanta specified in the frame (value between 0x0 and 0xFFFF).
        b) There is a valid class enable vector set on the frame - an 8-bit mask that specifies
            which 802.1p priority levels should be paused.
        c) The destination MAC address on the frame is "01:80:c2:00:00:01"
        d) The source MAC address on the frame is of the DUT port

    Args:
        snappi_api (pytest fixture): SNAPPI session
        snappi_testbed_config (pytest fixture): testbed configuration information
        conn_graph_facts (pytest fixture): connection graph
        fanout_graph_facts (pytest fixture): fanout graph
        duthosts (pytest fixture): list of DUTs
        rand_one_dut_hostname (str): hostname of DUT
        rand_one_dut_portname_oper_up (str): port to test, e.g., 's6100-1|Ethernet0'
        lossless_prio_list (pytest fixture): list of all the lossless priorities
        prio_dscp_map (pytest fixture): priority vs. DSCP map (key = priority).

    Returns:
        N/A
    """

    dut_hostname, dut_port = rand_one_dut_portname_oper_up.split('|')
    pytest_require(rand_one_dut_hostname == dut_hostname,
                   "Port is not mapped to the expected DUT")

    testbed_config, port_config_list = snappi_testbed_config
    duthost = duthosts[rand_one_dut_hostname]

    if not is_cisco_device(duthost):
        pytest.skip("Test is supported on Cisco device only")

    if is_snappi_multidut(duthosts):
        pytest.skip("Test is not supported on multi-dut")

    pause_prio_list = lossless_prio_list
    test_prio_list = lossless_prio_list

    snappi_extra_params = SnappiTestParams()
    snappi_extra_params.packet_capture_type = packet_capture.PFC_CAPTURE
    snappi_extra_params.is_snappi_ingress_port_cap = False

    run_pfc_valid_src_mac_test(
                    api=snappi_api,
                    testbed_config=testbed_config,
                    port_config_list=port_config_list,
                    conn_data=conn_graph_facts,
                    fanout_data=fanout_graph_facts,
                    duthost=duthost,
                    dut_port=dut_port,
                    global_pause=False,
                    pause_prio_list=pause_prio_list,
                    test_prio_list=test_prio_list,
                    prio_dscp_map=prio_dscp_map,
                    test_traffic_pause=True,
                    snappi_extra_params=snappi_extra_params)

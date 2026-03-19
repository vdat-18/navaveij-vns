"""Main entry point for the Navaveij Clinical MCP Server."""

from mcp.server.fastmcp import FastMCP

from src.mcp_server.tools.biomarker_trends import get_biomarker_trends
from src.mcp_server.tools.clinical_signals import get_clinical_signals
from src.mcp_server.tools.hard_constraints import get_hard_constraints
from src.mcp_server.tools.patient_event_timeline import get_patient_event_timeline
from src.mcp_server.tools.program_ruleset import get_program_ruleset

# Initialize FastMCP server
mcp = FastMCP("Navaveij Clinical Server")

# Register tools
mcp.tool()(get_hard_constraints)
mcp.tool()(get_clinical_signals)
mcp.tool()(get_biomarker_trends)
mcp.tool()(get_program_ruleset)
mcp.tool()(get_patient_event_timeline)

if __name__ == "__main__":
    mcp.run(transport="stdio")

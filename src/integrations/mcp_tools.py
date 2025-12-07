"""
MCP (Model Context Protocol) Tools Integration
==============================================

Implements MCP server and tool registry for external integrations.
MCP enables standardized communication between AI models and external tools.

Features:
- MCP server for exposing Growth Engine capabilities
- Tool registry for external MCP tools
- Bidirectional tool invocation
- Schema validation and error handling

Reference: https://modelcontextprotocol.io/
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional, Awaitable, TypeVar, Generic
from collections.abc import AsyncIterator

from pydantic import BaseModel, Field


# =============================================================================
# MCP PROTOCOL TYPES
# =============================================================================

class MCPMessageType(Enum):
    """MCP message types."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MCPErrorCode(Enum):
    """Standard MCP error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    TOOL_EXECUTION_ERROR = -32000


class MCPToolSchema(BaseModel):
    """Schema definition for an MCP tool."""
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)


class MCPRequest(BaseModel):
    """MCP request message."""
    jsonrpc: str = "2.0"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    method: str
    params: dict[str, Any] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    """MCP response message."""
    jsonrpc: str = "2.0"
    id: str
    result: Optional[dict[str, Any]] = None
    error: Optional[dict[str, Any]] = None


class MCPNotification(BaseModel):
    """MCP notification (no response expected)."""
    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# MCP TOOL INTERFACE
# =============================================================================

T = TypeVar('T')


class MCPTool(ABC, Generic[T]):
    """
    Abstract base class for MCP tools.
    
    Implement this to create tools that can be exposed via MCP.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (unique identifier)."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description."""
        pass
    
    @property
    def input_schema(self) -> dict[str, Any]:
        """JSON Schema for input parameters."""
        return {"type": "object", "properties": {}}
    
    @property
    def output_schema(self) -> dict[str, Any]:
        """JSON Schema for output."""
        return {"type": "object"}
    
    @abstractmethod
    async def execute(self, params: dict[str, Any]) -> T:
        """Execute the tool with given parameters."""
        pass
    
    def to_schema(self) -> MCPToolSchema:
        """Convert to MCPToolSchema."""
        return MCPToolSchema(
            name=self.name,
            description=self.description,
            input_schema=self.input_schema,
            output_schema=self.output_schema,
        )


# =============================================================================
# BUILT-IN GROWTH ENGINE MCP TOOLS
# =============================================================================

class DiscoverOpportunitiesTool(MCPTool[dict]):
    """MCP tool for discovering opportunities."""
    
    @property
    def name(self) -> str:
        return "growth_engine.discover_opportunities"
    
    @property
    def description(self) -> str:
        return "Search for career opportunities (jobs, grants, fellowships, etc.) based on criteria"
    
    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for opportunities"
                },
                "type": {
                    "type": "string",
                    "enum": ["job", "grant", "fellowship", "scholarship", "accelerator"],
                    "description": "Type of opportunity to search for"
                },
                "location": {
                    "type": "string",
                    "description": "Location filter (e.g., 'Remote', 'San Francisco')"
                },
                "min_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Minimum fit score threshold"
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                    "description": "Maximum number of results"
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, params: dict[str, Any]) -> dict:
        """Execute opportunity discovery."""
        try:
            from src.orchestrator import growth_engine
            
            result = await growth_engine.discover_opportunities(
                query=params.get("query", ""),
                opportunity_type=params.get("type"),
                location=params.get("location"),
                min_score=params.get("min_score", 0.0),
                limit=params.get("limit", 20),
            )
            
            return {
                "success": True,
                "opportunities": result if isinstance(result, list) else [result],
                "count": len(result) if isinstance(result, list) else 1,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class GenerateApplicationTool(MCPTool[dict]):
    """MCP tool for generating application content."""
    
    @property
    def name(self) -> str:
        return "growth_engine.generate_application"
    
    @property
    def description(self) -> str:
        return "Generate application content (cover letter, essay, proposal) for an opportunity"
    
    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "opportunity_id": {
                    "type": "string",
                    "description": "ID of the opportunity to apply for"
                },
                "content_type": {
                    "type": "string",
                    "enum": ["cover_letter", "essay", "proposal", "statement"],
                    "description": "Type of content to generate"
                },
                "prompt": {
                    "type": "string",
                    "description": "Optional custom prompt or essay question"
                },
                "word_limit": {
                    "type": "integer",
                    "description": "Maximum word count"
                },
                "tone": {
                    "type": "string",
                    "enum": ["professional", "conversational", "academic", "enthusiastic"],
                    "default": "professional"
                }
            },
            "required": ["opportunity_id", "content_type"]
        }
    
    async def execute(self, params: dict[str, Any]) -> dict:
        """Execute application generation."""
        try:
            from src.orchestrator import growth_engine
            
            result = await growth_engine.generate_application(
                opportunity_id=params["opportunity_id"],
                content_type=params["content_type"],
                prompt=params.get("prompt"),
                word_limit=params.get("word_limit"),
                tone=params.get("tone", "professional"),
            )
            
            return {
                "success": True,
                "content": result.get("content", ""),
                "word_count": result.get("word_count", 0),
                "quality_score": result.get("quality_score", 0),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class ScoreOpportunityTool(MCPTool[dict]):
    """MCP tool for scoring opportunity fit."""
    
    @property
    def name(self) -> str:
        return "growth_engine.score_opportunity"
    
    @property
    def description(self) -> str:
        return "Calculate fit score for an opportunity based on your profile"
    
    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "opportunity": {
                    "type": "object",
                    "description": "Opportunity data to score",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "requirements": {"type": "array", "items": {"type": "string"}},
                        "organization": {"type": "string"},
                    }
                },
                "opportunity_id": {
                    "type": "string",
                    "description": "ID of existing opportunity to score"
                }
            }
        }
    
    async def execute(self, params: dict[str, Any]) -> dict:
        """Execute opportunity scoring."""
        try:
            from src.scoring import ScoringEngine
            
            engine = ScoringEngine()
            
            if "opportunity_id" in params:
                # Score existing opportunity
                score = await engine.score_by_id(params["opportunity_id"])
            else:
                # Score provided opportunity data
                score = await engine.score_opportunity(params.get("opportunity", {}))
            
            return {
                "success": True,
                "fit_score": score.get("fit_score", 0),
                "tier": score.get("tier", "TIER_3"),
                "breakdown": score.get("breakdown", {}),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class GetAnalyticsTool(MCPTool[dict]):
    """MCP tool for retrieving analytics."""
    
    @property
    def name(self) -> str:
        return "growth_engine.get_analytics"
    
    @property
    def description(self) -> str:
        return "Get analytics and insights about your opportunity pipeline"
    
    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": ["day", "week", "month", "all"],
                    "default": "week",
                    "description": "Time period for analytics"
                },
                "include_recommendations": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include AI-generated recommendations"
                }
            }
        }
    
    async def execute(self, params: dict[str, Any]) -> dict:
        """Execute analytics retrieval."""
        try:
            from src.intelligence.analytics import AnalyticsEngine
            
            engine = AnalyticsEngine()
            
            period = params.get("period", "week")
            dashboard = await engine.get_dashboard(
                period=period,
                include_recommendations=params.get("include_recommendations", True)
            )
            
            return {
                "success": True,
                "period": period,
                "metrics": dashboard,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# =============================================================================
# MCP TOOL REGISTRY
# =============================================================================

class MCPToolRegistry:
    """
    Registry for MCP tools.
    
    Manages tool registration, lookup, and schema generation.
    """
    
    def __init__(self):
        """Initialize the registry."""
        self._tools: dict[str, MCPTool] = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self) -> None:
        """Register built-in Growth Engine tools."""
        builtin_tools = [
            DiscoverOpportunitiesTool(),
            GenerateApplicationTool(),
            ScoreOpportunityTool(),
            GetAnalyticsTool(),
        ]
        
        for tool in builtin_tools:
            self.register(tool)
    
    def register(self, tool: MCPTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
    
    def unregister(self, name: str) -> bool:
        """Unregister a tool."""
        if name in self._tools:
            del self._tools[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> list[MCPToolSchema]:
        """List all registered tools."""
        return [tool.to_schema() for tool in self._tools.values()]
    
    async def execute(self, name: str, params: dict[str, Any]) -> dict:
        """Execute a tool by name."""
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        return await tool.execute(params)


# =============================================================================
# MCP SERVER
# =============================================================================

class MCPServer:
    """
    MCP Server implementation for Growth Engine.
    
    Exposes Growth Engine capabilities via the Model Context Protocol.
    Can be used by other AI systems to interact with Growth Engine.
    """
    
    def __init__(
        self,
        name: str = "growth-engine",
        version: str = "1.0.0",
        registry: Optional[MCPToolRegistry] = None
    ):
        """
        Initialize MCP server.
        
        Args:
            name: Server name
            version: Server version
            registry: Tool registry (creates default if not provided)
        """
        self.name = name
        self.version = version
        self.registry = registry or MCPToolRegistry()
        
        self._handlers: dict[str, Callable] = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_list_tools,
            "tools/call": self._handle_call_tool,
            "ping": self._handle_ping,
        }
    
    async def handle_message(self, message: str) -> str:
        """
        Handle an incoming MCP message.
        
        Args:
            message: JSON-encoded MCP message
            
        Returns:
            JSON-encoded MCP response
        """
        try:
            data = json.loads(message)
            request = MCPRequest.model_validate(data)
            
            handler = self._handlers.get(request.method)
            if not handler:
                return self._error_response(
                    request.id,
                    MCPErrorCode.METHOD_NOT_FOUND,
                    f"Unknown method: {request.method}"
                )
            
            result = await handler(request.params)
            
            response = MCPResponse(
                id=request.id,
                result=result
            )
            return response.model_dump_json()
            
        except json.JSONDecodeError as e:
            return self._error_response("", MCPErrorCode.PARSE_ERROR, str(e))
        except Exception as e:
            return self._error_response("", MCPErrorCode.INTERNAL_ERROR, str(e))
    
    async def handle_stream(
        self,
        reader: AsyncIterator[str]
    ) -> AsyncIterator[str]:
        """
        Handle a stream of MCP messages.
        
        Args:
            reader: Async iterator of incoming messages
            
        Yields:
            Response messages
        """
        async for message in reader:
            response = await self.handle_message(message)
            yield response
    
    async def _handle_initialize(self, params: dict) -> dict:
        """Handle initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version
            }
        }
    
    async def _handle_list_tools(self, params: dict) -> dict:
        """Handle tools/list request."""
        tools = self.registry.list_tools()
        return {
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.input_schema,
                }
                for t in tools
            ]
        }
    
    async def _handle_call_tool(self, params: dict) -> dict:
        """Handle tools/call request."""
        tool_name = params.get("name")
        tool_params = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Tool name required")
        
        result = await self.registry.execute(tool_name, tool_params)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    
    async def _handle_ping(self, params: dict) -> dict:
        """Handle ping request."""
        return {"pong": True, "timestamp": datetime.utcnow().isoformat()}
    
    def _error_response(
        self,
        request_id: str,
        code: MCPErrorCode,
        message: str
    ) -> str:
        """Create an error response."""
        response = MCPResponse(
            id=request_id,
            error={
                "code": code.value,
                "message": message
            }
        )
        return response.model_dump_json()


# =============================================================================
# MCP CLIENT
# =============================================================================

class MCPClient:
    """
    MCP Client for connecting to external MCP servers.
    
    Allows Growth Engine to use tools from other MCP-compatible services.
    """
    
    def __init__(self, server_url: str):
        """
        Initialize MCP client.
        
        Args:
            server_url: URL of the MCP server
        """
        self.server_url = server_url
        self._request_id = 0
        self._initialized = False
        self._available_tools: list[dict] = []
    
    async def connect(self) -> bool:
        """
        Connect and initialize with the MCP server.
        
        Returns:
            True if connection successful
        """
        try:
            response = await self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "growth-engine-client",
                    "version": "1.0.0"
                }
            })
            
            if "error" not in response:
                self._initialized = True
                # Fetch available tools
                await self.refresh_tools()
                return True
            
            return False
            
        except Exception:
            return False
    
    async def refresh_tools(self) -> list[dict]:
        """Refresh the list of available tools."""
        response = await self._send_request("tools/list", {})
        self._available_tools = response.get("tools", [])
        return self._available_tools
    
    async def call_tool(self, name: str, arguments: dict) -> dict:
        """
        Call a tool on the remote MCP server.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self._initialized:
            raise RuntimeError("Client not initialized. Call connect() first.")
        
        response = await self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        
        return response
    
    async def _send_request(self, method: str, params: dict) -> dict:
        """Send a request to the MCP server."""
        import httpx
        
        self._request_id += 1
        
        request = MCPRequest(
            id=str(self._request_id),
            method=method,
            params=params
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.server_url,
                json=request.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            if "error" in data:
                raise RuntimeError(f"MCP Error: {data['error']}")
            
            return data.get("result", {})
    
    @property
    def tools(self) -> list[dict]:
        """Get available tools."""
        return self._available_tools


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_mcp_server(
    include_builtin_tools: bool = True,
    custom_tools: Optional[list[MCPTool]] = None
) -> MCPServer:
    """
    Create an MCP server instance.
    
    Args:
        include_builtin_tools: Include built-in Growth Engine tools
        custom_tools: Additional custom tools to register
        
    Returns:
        Configured MCPServer
    """
    registry = MCPToolRegistry() if include_builtin_tools else MCPToolRegistry.__new__(MCPToolRegistry)
    
    if not include_builtin_tools:
        registry._tools = {}
    
    if custom_tools:
        for tool in custom_tools:
            registry.register(tool)
    
    return MCPServer(registry=registry)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Types
    'MCPMessageType',
    'MCPErrorCode',
    'MCPToolSchema',
    'MCPRequest',
    'MCPResponse',
    'MCPNotification',
    
    # Tool base class
    'MCPTool',
    
    # Built-in tools
    'DiscoverOpportunitiesTool',
    'GenerateApplicationTool',
    'ScoreOpportunityTool',
    'GetAnalyticsTool',
    
    # Registry and server
    'MCPToolRegistry',
    'MCPServer',
    'MCPClient',
    
    # Factory
    'create_mcp_server',
]

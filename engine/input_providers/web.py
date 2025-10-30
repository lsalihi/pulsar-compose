"""
Web input provider for HTTP API interactions.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
import aiohttp
from aiohttp import web
import threading
import time
from urllib.parse import urlparse

from .base import InputProvider, InteractionRequest, InteractionResponse, ValidationError


class WebInputProvider(InputProvider):
    """Input provider for web-based interactions via HTTP API."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.host = config.get('host', 'localhost') if config else 'localhost'
        self.port = config.get('port', 8080) if config else 8080
        self.base_url = config.get('base_url', f'http://{self.host}:{self.port}') if config else f'http://{self.host}:{self.port}'
        self.session_timeout = config.get('session_timeout', 300) if config else 300  # 5 minutes
        self.server = None
        self.site = None
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def can_handle(self, request: InteractionRequest) -> bool:
        """Check if this provider can handle web interactions."""
        return True

    async def get_input(self, request: InteractionRequest) -> InteractionResponse:
        """Get input via web interface."""
        # Generate unique session ID
        session_id = f"session_{int(time.time() * 1000)}_{hash(str(request)) % 10000}"

        # Create a future for the response
        future = asyncio.Future()
        self.pending_requests[session_id] = future

        # Store session data
        self.active_sessions[session_id] = {
            'request': request,
            'created_at': time.time(),
            'status': 'waiting'
        }

        try:
            # Start server if not running
            await self._ensure_server_running()

            # Generate interaction URL
            interaction_url = f"{self.base_url}/interact/{session_id}"

            print(f"User interaction required. Please visit: {interaction_url}")
            print("Waiting for user input...")

            # Wait for response with timeout
            timeout = request.timeout or self.session_timeout
            response = await asyncio.wait_for(future, timeout=timeout)

            return response

        except asyncio.TimeoutError:
            raise ValidationError("interaction", f"Input timeout after {timeout} seconds")
        except Exception as e:
            raise ValidationError("interaction", f"Web input error: {str(e)}")
        finally:
            # Clean up
            self.pending_requests.pop(session_id, None)
            self.active_sessions.pop(session_id, None)

    async def _ensure_server_running(self):
        """Ensure the web server is running."""
        if self.server is None:
            self.server = web.Application()
            self.server.router.add_get('/interact/{session_id}', self._handle_interaction_page)
            self.server.router.add_post('/interact/{session_id}/submit', self._handle_interaction_submit)
            self.server.router.add_get('/health', self._handle_health)

            runner = web.AppRunner(self.server)
            await runner.setup()

            try:
                self.site = web.TCPSite(runner, self.host, self.port)
                await self.site.start()
                print(f"Web input server started at {self.base_url}")
            except OSError as e:
                print(f"Failed to start web server: {e}")
                print("Falling back to console input would be ideal here, but for now raising error")
                raise

    async def _handle_interaction_page(self, request):
        """Serve the interaction HTML page."""
        session_id = request.match_info['session_id']

        if session_id not in self.active_sessions:
            return web.Response(text="Session not found or expired", status=404)

        session_data = self.active_sessions[session_id]
        interaction_request = session_data['request']

        # Generate HTML form
        html = self._generate_html_form(session_id, interaction_request)

        return web.Response(text=html, content_type='text/html')

    async def _handle_interaction_submit(self, request):
        """Handle form submission."""
        session_id = request.match_info['session_id']

        if session_id not in self.pending_requests:
            return web.json_response({'error': 'Session not found or expired'}, status=404)

        try:
            data = await request.post()
            answers = {}

            # Parse form data
            session_data = self.active_sessions[session_id]
            interaction_request = session_data['request']

            for i, question in enumerate(interaction_request.questions):
                field_name = f"question_{i}"
                answer = data.get(field_name)

                if answer is not None:
                    # Handle multiple choice with multiple selections
                    if question.multiple and isinstance(answer, list):
                        answers[field_name] = answer
                    elif question.type.value == 'number':
                        try:
                            answers[field_name] = float(answer) if '.' in str(answer) else int(answer)
                        except ValueError:
                            answers[field_name] = answer
                    elif question.type.value == 'boolean':
                        answers[field_name] = answer.lower() in ('true', '1', 'yes', 'on')
                    else:
                        answers[field_name] = answer

            # Validate response
            response = InteractionResponse(
                answers=answers,
                metadata={'provider': 'web', 'session_id': session_id}
            )

            self.validate_response(interaction_request, response)

            # Complete the future
            self.pending_requests[session_id].set_result(response)

            # Return success page
            return web.Response(text="<h1>Thank you! Your responses have been recorded.</h1>", content_type='text/html')

        except ValidationError as e:
            return web.json_response({'error': str(e)}, status=400)
        except Exception as e:
            return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)

    async def _handle_health(self, request):
        """Health check endpoint."""
        return web.json_response({
            'status': 'healthy',
            'active_sessions': len(self.active_sessions),
            'pending_requests': len(self.pending_requests)
        })

    def _generate_html_form(self, session_id: str, request: InteractionRequest) -> str:
        """Generate HTML form for the interaction."""
        title = request.metadata.get('title', 'User Interaction Required') if request.metadata else 'User Interaction Required'
        description = request.metadata.get('description', '') if request.metadata else ''

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .question {{ margin-bottom: 20px; }}
        .question label {{ display: block; font-weight: bold; margin-bottom: 5px; }}
        .question input, .question select, .question textarea {{
            width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;
        }}
        .question textarea {{ height: 100px; }}
        .options {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .option {{ display: flex; align-items: center; }}
        .submit-btn {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
        .submit-btn:hover {{ background: #0056b3; }}
        .required {{ color: red; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {f'<p>{description}</p>' if description else ''}

    <form method="post" action="/interact/{session_id}/submit">
"""

        for i, question in enumerate(request.questions):
            field_name = f"question_{i}"
            required_mark = '<span class="required">*</span>' if question.required else ''

            html += f'<div class="question">'
            html += f'<label>{question.question}{required_mark}</label>'

            if question.type.value == 'text':
                placeholder = question.placeholder or ''
                default_value = question.default or ''
                html += f'<textarea name="{field_name}" placeholder="{placeholder}">{default_value}</textarea>'

            elif question.type.value == 'multiple_choice':
                if question.multiple:
                    html += '<div class="options">'
                    for option in question.options or []:
                        checked = 'checked' if question.default and option in question.default else ''
                        html += f'''
                        <label class="option">
                            <input type="checkbox" name="{field_name}" value="{option}" {checked}>
                            {option}
                        </label>'''
                    html += '</div>'
                else:
                    html += f'<select name="{field_name}">'
                    if not question.required:
                        html += '<option value="">-- Select --</option>'
                    for option in question.options or []:
                        selected = 'selected' if question.default == option else ''
                        html += f'<option value="{option}" {selected}>{option}</option>'
                    html += '</select>'

            elif question.type.value == 'number':
                default_value = question.default or ''
                html += f'<input type="number" name="{field_name}" value="{default_value}">'

            elif question.type.value == 'boolean':
                checked = 'checked' if question.default else ''
                html += f'<input type="checkbox" name="{field_name}" {checked}>'

            html += '</div>'

        html += '''
        <button type="submit" class="submit-btn">Submit</button>
    </form>
</body>
</html>'''

        return html

    async def cleanup(self):
        """Clean up resources."""
        if self.site:
            await self.site.stop()
            self.site = None
        if self.server:
            self.server = None
        self.pending_requests.clear()
        self.active_sessions.clear()
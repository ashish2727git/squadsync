"""
WebRTC configuration endpoint for TURN/STUN servers
"""
from fastapi import APIRouter, Depends
from backend.core.dependencies import get_current_user
from backend.models.models import User
from backend.integrations.twilio_service import twilio_service

router = APIRouter(prefix="/webrtc", tags=["webrtc"])

@router.get("/ice-servers")
async def get_ice_servers(current_user: User = Depends(get_current_user)):
    """
    Get ICE servers configuration for WebRTC
    Returns Twilio TURN servers for better quality if configured,
    otherwise returns free STUN servers
    """
    ice_config = twilio_service.get_ice_servers()
    
    return {
        "iceServers": ice_config.get('iceServers', []),
        "username": current_user.username
    }

@router.get("/turn-credentials")
async def get_turn_credentials(current_user: User = Depends(get_current_user)):
    """
    Generate TURN credentials for current user
    Provides better connection quality through relay servers
    """
    credentials = twilio_service.generate_turn_credentials(current_user.username)
    
    return credentials

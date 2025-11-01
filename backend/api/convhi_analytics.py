#!/usr/bin/env python3
"""
ConvHi Analytics Dashboard - Sistema d'anàlisi en temps real
Dashboard complet amb mètriques de rendiment, anàlisi de converses i insights
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, Counter

logger = logging.getLogger("veuplus.analytics")

router = APIRouter(prefix="/api/convhi/analytics", tags=["ConvHi Analytics"])

# Models
class AnalyticsTimeRange(BaseModel):
    start_date: datetime
    end_date: datetime
    period: str = "day"  # hour, day, week, month

class ConversationMetrics(BaseModel):
    total_conversations: int
    successful_conversations: int
    failed_conversations: int
    average_duration: float
    average_response_time: float
    total_messages: int
    average_messages_per_conversation: float

class AgentPerformance(BaseModel):
    agent_id: str
    agent_name: str
    total_interactions: int
    success_rate: float
    average_response_time: float
    user_satisfaction: float
    knowledge_usage_rate: float
    language_breakdown: Dict[str, int]

class LanguageBreakdown(BaseModel):
    language: str
    percentage: float
    total_calls: int
    average_duration: float

class RealTimeMetrics(BaseModel):
    active_calls: int
    calls_today: int
    average_wait_time: float
    system_health: Dict[str, bool]
    top_agents: List[Dict[str, Any]]


class ConversationTimeline(BaseModel):
    date: str
    total: int
    completed: int
    failed: int

# In-memory analytics storage (en producció usar base de dades)
analytics_data = {
    "conversations": [],
    "interactions": [],
    "performance_metrics": {},
    "real_time_stats": {
        "active_calls": 0,
        "calls_today": 0,
        "system_health": {
            "asr": True,
            "llm": True,
            "tts": True,
            "knowledge_base": True
        }
    }
}

class AnalyticsEngine:
    def __init__(self):
        self.metrics_cache = {}
        self.real_time_data = {}
    
    async def log_conversation(self, conversation_data: Dict[str, Any]):
        """Registrar nova conversa per anàlisi"""
        try:
            conversation_record = {
                "id": conversation_data.get("id", f"conv_{len(analytics_data['conversations']) + 1}"),
                "agent_id": conversation_data.get("agent_id"),
                "user_id": conversation_data.get("user_id", "anonymous"),
                "start_time": conversation_data.get("start_time", datetime.now().isoformat()),
                "end_time": conversation_data.get("end_time"),
                "duration": conversation_data.get("duration", 0),
                "status": conversation_data.get("status", "completed"),  # completed, failed, interrupted
                "total_messages": conversation_data.get("total_messages", 0),
                "language": conversation_data.get("language", "unknown"),
                "satisfaction_score": conversation_data.get("satisfaction_score"),
                "knowledge_used": conversation_data.get("knowledge_used", 0),
                "llm_provider": conversation_data.get("llm_provider"),
                "voice_system": conversation_data.get("voice_system"),
                "metadata": conversation_data.get("metadata", {})
            }
            
            analytics_data["conversations"].append(conversation_record)
            
            # Actualitzar estadístiques en temps real
            await self._update_real_time_stats(conversation_record)
            
            logger.info(f"📊 Conversa registrada: {conversation_record['id']}")
            
        except Exception as e:
            logger.error(f"Error registrant conversa: {e}")
    
    async def log_interaction(self, interaction_data: Dict[str, Any]):
        """Registrar interacció individual"""
        try:
            interaction_record = {
                "id": interaction_data.get("id", f"int_{len(analytics_data['interactions']) + 1}"),
                "conversation_id": interaction_data.get("conversation_id"),
                "agent_id": interaction_data.get("agent_id"),
                "timestamp": interaction_data.get("timestamp", datetime.now().isoformat()),
                "message_type": interaction_data.get("message_type", "text"),  # text, audio
                "user_message": interaction_data.get("user_message", ""),
                "agent_response": interaction_data.get("agent_response", ""),
                "response_time": interaction_data.get("response_time", 0),
                "success": interaction_data.get("success", True),
                "knowledge_used": interaction_data.get("knowledge_used", 0),
                "llm_tokens": interaction_data.get("llm_tokens", 0),
                "audio_duration": interaction_data.get("audio_duration", 0)
            }
            
            analytics_data["interactions"].append(interaction_record)
            
            logger.info(f"📊 Interacció registrada: {interaction_record['id']}")
            
        except Exception as e:
            logger.error(f"Error registrant interacció: {e}")
    
    async def _update_real_time_stats(self, conversation: Dict[str, Any]):
        """Actualitzar estadístiques en temps real"""
        try:
            # Actualitzar trucades avui
            today = datetime.now().date()
            conversation_date = datetime.fromisoformat(conversation["start_time"]).date()
            
            if conversation_date == today:
                analytics_data["real_time_stats"]["calls_today"] += 1
            
            # Actualitzar trucades actives (simulació)
            if conversation["status"] == "active":
                analytics_data["real_time_stats"]["active_calls"] += 1
            elif conversation["status"] in ["completed", "failed"]:
                analytics_data["real_time_stats"]["active_calls"] = max(0, 
                    analytics_data["real_time_stats"]["active_calls"] - 1)
            
        except Exception as e:
            logger.error(f"Error actualitzant estadístiques temps real: {e}")
    
    async def get_conversation_metrics(self, time_range: AnalyticsTimeRange) -> ConversationMetrics:
        """Obtenir mètriques de converses"""
        try:
            start_date = time_range.start_date
            end_date = time_range.end_date
            
            # Filtrar converses per rang de dates
            filtered_conversations = [
                conv for conv in analytics_data["conversations"]
                if start_date <= datetime.fromisoformat(conv["start_time"]) <= end_date
            ]
            
            if not filtered_conversations:
                return ConversationMetrics(
                    total_conversations=0,
                    successful_conversations=0,
                    failed_conversations=0,
                    average_duration=0.0,
                    average_response_time=0.0,
                    total_messages=0,
                    average_messages_per_conversation=0.0
                )
            
            # Calcular mètriques
            total_conversations = len(filtered_conversations)
            successful_conversations = len([c for c in filtered_conversations if c["status"] == "completed"])
            failed_conversations = total_conversations - successful_conversations
            
            durations = [c["duration"] for c in filtered_conversations if c["duration"] > 0]
            average_duration = statistics.mean(durations) if durations else 0.0
            
            total_messages = sum(c["total_messages"] for c in filtered_conversations)
            average_messages_per_conversation = total_messages / total_conversations if total_conversations > 0 else 0.0
            
            # Calcular temps de resposta mitjà
            response_times = []
            for conv in filtered_conversations:
                conv_interactions = [
                    i for i in analytics_data["interactions"]
                    if i["conversation_id"] == conv["id"]
                ]
                response_times.extend([i["response_time"] for i in conv_interactions if i["response_time"] > 0])
            
            average_response_time = statistics.mean(response_times) if response_times else 0.0
            
            return ConversationMetrics(
                total_conversations=total_conversations,
                successful_conversations=successful_conversations,
                failed_conversations=failed_conversations,
                average_duration=average_duration,
                average_response_time=average_response_time,
                total_messages=total_messages,
                average_messages_per_conversation=average_messages_per_conversation
            )
            
        except Exception as e:
            logger.error(f"Error calculant mètriques de converses: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_agent_performance(self, agent_id: Optional[str] = None) -> List[AgentPerformance]:
        """Obtenir rendiment dels agents"""
        try:
            agent_performance = {}
            
            # Agrupar per agent
            for conv in analytics_data["conversations"]:
                agent_id_key = conv["agent_id"]
                if agent_id and agent_id_key != agent_id:
                    continue
                
                if agent_id_key not in agent_performance:
                    agent_performance[agent_id_key] = {
                        "agent_id": agent_id_key,
                        "agent_name": f"Agent {agent_id_key}",
                        "total_interactions": 0,
                        "successful_interactions": 0,
                        "response_times": [],
                        "satisfaction_scores": [],
                        "knowledge_usage": 0,
                        "languages": Counter()
                    }
                
                perf = agent_performance[agent_id_key]
                perf["total_interactions"] += 1
                
                if conv["status"] == "completed":
                    perf["successful_interactions"] += 1
                
                perf["knowledge_usage"] += conv.get("knowledge_used", 0)
                perf["languages"][conv.get("language", "unknown")] += 1
                
                if conv.get("satisfaction_score"):
                    perf["satisfaction_scores"].append(conv["satisfaction_score"])
            
            # Calcular mètriques finals
            results = []
            for agent_id_key, perf in agent_performance.items():
                success_rate = (perf["successful_interactions"] / perf["total_interactions"] * 100) if perf["total_interactions"] > 0 else 0
                average_response_time = statistics.mean(perf["response_times"]) if perf["response_times"] else 0.0
                user_satisfaction = statistics.mean(perf["satisfaction_scores"]) if perf["satisfaction_scores"] else 0.0
                knowledge_usage_rate = (perf["knowledge_usage"] / perf["total_interactions"] * 100) if perf["total_interactions"] > 0 else 0
                
                results.append(AgentPerformance(
                    agent_id=agent_id_key,
                    agent_name=perf["agent_name"],
                    total_interactions=perf["total_interactions"],
                    success_rate=success_rate,
                    average_response_time=average_response_time,
                    user_satisfaction=user_satisfaction,
                    knowledge_usage_rate=knowledge_usage_rate,
                    language_breakdown=dict(perf["languages"])
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculant rendiment d'agents: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_language_breakdown(self, time_range: AnalyticsTimeRange) -> List[LanguageBreakdown]:
        """Obtenir desglossament per idiomes"""
        try:
            start_date = time_range.start_date
            end_date = time_range.end_date
            
            # Filtrar converses per rang de dates
            filtered_conversations = [
                conv for conv in analytics_data["conversations"]
                if start_date <= datetime.fromisoformat(conv["start_time"]) <= end_date
            ]
            
            # Agrupar per idioma
            language_stats = defaultdict(lambda: {"calls": 0, "durations": []})
            
            for conv in filtered_conversations:
                language = conv.get("language", "unknown")
                language_stats[language]["calls"] += 1
                if conv["duration"] > 0:
                    language_stats[language]["durations"].append(conv["duration"])
            
            # Calcular percentatges i mitjanes
            total_calls = len(filtered_conversations)
            results = []
            
            for language, stats in language_stats.items():
                percentage = (stats["calls"] / total_calls * 100) if total_calls > 0 else 0
                average_duration = statistics.mean(stats["durations"]) if stats["durations"] else 0.0
                
                results.append(LanguageBreakdown(
                    language=language,
                    percentage=percentage,
                    total_calls=stats["calls"],
                    average_duration=average_duration
                ))
            
            # Ordenar per percentatge descendent
            results.sort(key=lambda x: x.percentage, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculant desglossament d'idiomes: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_conversation_timeline(self, days: int = 30, agent_id: Optional[str] = None) -> List[ConversationTimeline]:
        """Obtenir timeline de converses"""
        try:
            end_date = datetime.now().date()
            days = max(1, min(days, 90))
            start_date = end_date - timedelta(days=days - 1)

            timeline: Dict[str, Dict[str, int]] = {}
            current = start_date
            while current <= end_date:
                timeline[current.isoformat()] = {"total": 0, "completed": 0, "failed": 0}
                current += timedelta(days=1)

            for conversation in analytics_data["conversations"]:
                try:
                    start_time = datetime.fromisoformat(conversation.get("start_time"))
                except Exception:
                    continue

                day_key = start_time.date().isoformat()
                if day_key not in timeline:
                    continue

                if agent_id and conversation.get("agent_id") != agent_id:
                    continue

                timeline[day_key]["total"] += 1
                status = (conversation.get("status") or "").lower()
                if status == "completed":
                    timeline[day_key]["completed"] += 1
                elif status == "failed":
                    timeline[day_key]["failed"] += 1

            ordered: List[ConversationTimeline] = []
            current = start_date
            while current <= end_date:
                key = current.isoformat()
                bucket = timeline.get(key, {"total": 0, "completed": 0, "failed": 0})
                ordered.append(ConversationTimeline(date=key, total=bucket["total"], completed=bucket["completed"], failed=bucket["failed"]))
                current += timedelta(days=1)

            return ordered
        except Exception as exc:
            logger.error(f"Error generant timeline de converses: {exc}")
            raise HTTPException(status_code=500, detail=str(exc))

    async def get_real_time_metrics(self) -> RealTimeMetrics:
        """Obtenir mètriques en temps real"""
        try:
            # Obtenir top agents (simulació)
            top_agents = []
            agent_stats = defaultdict(int)
            
            for conv in analytics_data["conversations"][-100:]:  # Últimes 100 converses
                agent_stats[conv["agent_id"]] += 1
            
            for agent_id, count in sorted(agent_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                top_agents.append({
                    "agent_id": agent_id,
                    "agent_name": f"Agent {agent_id}",
                    "calls_today": count
                })
            
            return RealTimeMetrics(
                active_calls=analytics_data["real_time_stats"]["active_calls"],
                calls_today=analytics_data["real_time_stats"]["calls_today"],
                average_wait_time=0.5,  # Simulació
                system_health=analytics_data["real_time_stats"]["system_health"],
                top_agents=top_agents
            )
            
        except Exception as e:
            logger.error(f"Error obtenint mètriques temps real: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Instància global
analytics_engine = AnalyticsEngine()

# Endpoints
@router.get("/dashboard")
async def get_dashboard_data(
    period: str = Query("day", description="Període: hour, day, week, month"),
    agent_id: Optional[str] = Query(None, description="ID de l'agent específic")
):
    """Obtenir dades del dashboard principal"""
    try:
        # Definir rang de dates segons el període
        end_date = datetime.now()
        if period == "hour":
            start_date = end_date - timedelta(hours=1)
        elif period == "day":
            start_date = end_date - timedelta(days=1)
        elif period == "week":
            start_date = end_date - timedelta(weeks=1)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=1)
        
        time_range = AnalyticsTimeRange(
            start_date=start_date,
            end_date=end_date,
            period=period
        )
        
        # Obtenir totes les mètriques
        conversation_metrics = await analytics_engine.get_conversation_metrics(time_range)
        agent_performance = await analytics_engine.get_agent_performance(agent_id)
        language_breakdown = await analytics_engine.get_language_breakdown(time_range)
        real_time_metrics = await analytics_engine.get_real_time_metrics()
        
        return {
            "success": True,
            "period": period,
            "time_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "conversation_metrics": conversation_metrics.dict(),
            "agent_performance": [ap.dict() for ap in agent_performance],
            "language_breakdown": [lb.dict() for lb in language_breakdown],
            "real_time_metrics": real_time_metrics.dict()
        }
        
    except Exception as e:
        logger.error(f"Error obtenint dades del dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/timeline")
async def get_conversation_timeline_endpoint(
    days: int = Query(30, description="Dies a analitzar (1-90)"),
    agent_id: Optional[str] = Query(None, description="Agent opcional"),
):
    """Obtenir timeline agregat de converses"""
    try:
        timeline = await analytics_engine.get_conversation_timeline(days=days, agent_id=agent_id)
        return {
            "success": True,
            "timeline": [entry.dict() for entry in timeline],
            "days": days,
            "agent_id": agent_id,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error obtenint timeline de converses: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/metrics/conversations")
async def get_conversation_metrics_endpoint(
    start_date: datetime = Query(..., description="Data d'inici"),
    end_date: datetime = Query(..., description="Data de fi"),
    period: str = Query("day", description="Període")
):
    """Obtenir mètriques de converses"""
    try:
        time_range = AnalyticsTimeRange(
            start_date=start_date,
            end_date=end_date,
            period=period
        )
        
        metrics = await analytics_engine.get_conversation_metrics(time_range)
        
        return {
            "success": True,
            "metrics": metrics.dict(),
            "time_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "period": period
            }
        }
        
    except Exception as e:
        logger.error(f"Error obtenint mètriques de converses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/agents")
async def get_agent_performance_endpoint(
    agent_id: Optional[str] = Query(None, description="ID de l'agent específic")
):
    """Obtenir rendiment dels agents"""
    try:
        performance = await analytics_engine.get_agent_performance(agent_id)
        
        return {
            "success": True,
            "performance": [p.dict() for p in performance],
            "total_agents": len(performance)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint rendiment d'agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/languages")
async def get_language_breakdown_endpoint(
    start_date: datetime = Query(..., description="Data d'inici"),
    end_date: datetime = Query(..., description="Data de fi")
):
    """Obtenir desglossament per idiomes"""
    try:
        time_range = AnalyticsTimeRange(
            start_date=start_date,
            end_date=end_date
        )
        
        breakdown = await analytics_engine.get_language_breakdown(time_range)
        
        return {
            "success": True,
            "language_breakdown": [lb.dict() for lb in breakdown],
            "total_languages": len(breakdown)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint desglossament d'idiomes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime")
async def get_real_time_metrics_endpoint():
    """Obtenir mètriques en temps real"""
    try:
        metrics = await analytics_engine.get_real_time_metrics()
        
        return {
            "success": True,
            "metrics": metrics.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obtenint mètriques temps real: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log/conversation")
async def log_conversation(conversation_data: Dict[str, Any]):
    """Registrar nova conversa"""
    try:
        await analytics_engine.log_conversation(conversation_data)
        
        return {
            "success": True,
            "message": "Conversa registrada correctament"
        }
        
    except Exception as e:
        logger.error(f"Error registrant conversa: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log/interaction")
async def log_interaction(interaction_data: Dict[str, Any]):
    """Registrar nova interacció"""
    try:
        await analytics_engine.log_interaction(interaction_data)
        
        return {
            "success": True,
            "message": "Interacció registrada correctament"
        }
        
    except Exception as e:
        logger.error(f"Error registrant interacció: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def analytics_health():
    """Health check del sistema d'anàlisi"""
    return {
        "status": "ok",
        "message": "Sistema d'anàlisi funcionant",
        "data_points": {
            "conversations": len(analytics_data["conversations"]),
            "interactions": len(analytics_data["interactions"])
        },
        "timestamp": datetime.now().isoformat()
    }


"""
AI-assisted insights service.
Provides suggestions and analysis without modifying data.

Features:
- Deadline prioritization suggestions
- Summarization of long observation fields
- Risk flagging
"""
import os
from typing import Dict, List, Optional, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from . import models_sqlalchemy as models
from . import deadline_awareness


class AIInsightsService:
    """
    Service for generating AI-assisted insights.
    
    All insights are suggestions only - never modifies data automatically.
    """
    
    @staticmethod
    def suggest_prioritization(
        db: Session,
        process_id: int,
        alert_window_days: int = 7
    ) -> Dict[str, Any]:
        """
        Suggest prioritization based on deadline status.
        
        Args:
            db: Database session
            process_id: Process ID
            alert_window_days: Days ahead to consider as urgent
            
        Returns:
            Dictionary with prioritization suggestion
        """
        process = db.query(models.Process).filter(
            models.Process.id == process_id
        ).first()
        
        if not process:
            return {"error": "Process not found"}
        
        deadline_status = deadline_awareness.calculate_deadline_status(
            process.prazo_final,
            alert_window_days
        )
        
        priority_score = 0
        priority_level = "normal"
        reasons = []
        
        if deadline_status["status"] == "overdue":
            days_overdue = abs(deadline_status.get("days_until", 0))
            priority_score = 100 - min(days_overdue * 5, 95)
            priority_level = "critical"
            reasons.append(f"Prazo vencido há {days_overdue} dia(s)")
        elif deadline_status["status"] == "upcoming":
            days_until = deadline_status.get("days_until", 0)
            priority_score = 80 - (days_until * 5)
            priority_level = "high" if days_until <= 3 else "medium"
            reasons.append(f"Prazo próximo: {days_until} dia(s) restante(s)")
        else:
            priority_score = 30
            priority_level = "normal"
            reasons.append("Prazo dentro do normal")
        
        # Additional factors
        if not process.partes:
            priority_score += 5
            reasons.append("Informação de partes ausente")
        
        if not process.tema_observacoes:
            priority_score += 5
            reasons.append("Tema/observações ausente")
        
        if process.prazo_final and deadline_status["status"] == "ok":
            days_until = deadline_status.get("days_until", 0)
            if days_until <= 30:
                priority_score += 10
                reasons.append("Prazo dentro de 30 dias")
        
        priority_score = min(priority_score, 100)
        
        return {
            "process_id": process_id,
            "priority_score": priority_score,
            "priority_level": priority_level,
            "reasons": reasons,
            "deadline_status": deadline_status,
            "suggestion": f"Prioridade {priority_level.upper()}: {', '.join(reasons)}"
        }
    
    @staticmethod
    def summarize_observations(
        text: Optional[str],
        max_length: int = 150
    ) -> Dict[str, Any]:
        """
        Summarize long observation fields.
        
        Uses simple text processing if AI is not available,
        or AI summarization if configured.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Dictionary with summary and metadata
        """
        if not text or not text.strip():
            return {
                "original": None,
                "summary": None,
                "is_summarized": False,
                "original_length": 0
            }
        
        original_length = len(text)
        
        # Simple truncation-based summary (fallback)
        if original_length <= max_length:
            return {
                "original": text,
                "summary": text,
                "is_summarized": False,
                "original_length": original_length,
                "summary_length": original_length
            }
        
        # Try AI summarization if available
        ai_summary = AIInsightsService._ai_summarize(text, max_length)
        
        if ai_summary:
            return {
                "original": text,
                "summary": ai_summary,
                "is_summarized": True,
                "original_length": original_length,
                "summary_length": len(ai_summary),
                "compression_ratio": round(len(ai_summary) / original_length, 2)
            }
        
        # Fallback: intelligent truncation
        words = text.split()
        if len(words) <= 20:
            summary = text
        else:
            # Take first sentence or first 100 chars
            sentences = text.split('.')
            if sentences and len(sentences[0]) <= max_length:
                summary = sentences[0].strip() + '.'
            else:
                summary = text[:max_length].rsplit(' ', 1)[0] + '...'
        
        return {
            "original": text,
            "summary": summary,
            "is_summarized": True,
            "original_length": original_length,
            "summary_length": len(summary),
            "compression_ratio": round(len(summary) / original_length, 2),
            "method": "truncation"
        }
    
    @staticmethod
    def _ai_summarize(text: str, max_length: int) -> Optional[str]:
        """
        Attempt AI-based summarization.
        
        Supports OpenAI API or can be extended for other providers.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text or None if AI not available
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return None
        
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente jurídico. Resuma textos de processos administrativos de forma concisa e profissional, preservando informações importantes."
                    },
                    {
                        "role": "user",
                        "content": f"Resuma o seguinte texto em no máximo {max_length} caracteres, mantendo informações jurídicas relevantes:\n\n{text}"
                    }
                ],
                max_tokens=min(max_length // 4, 200),
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary if len(summary) <= max_length else summary[:max_length]
            
        except Exception as e:
            import logging
            logging.warning(f"AI summarization failed: {e}")
            return None
    
    @staticmethod
    def flag_potential_risks(
        db: Session,
        process_id: int
    ) -> Dict[str, Any]:
        """
        Flag potential risks in a process.
        
        Args:
            db: Database session
            process_id: Process ID
            
        Returns:
            Dictionary with risk flags and suggestions
        """
        process = db.query(models.Process).filter(
            models.Process.id == process_id
        ).first()
        
        if not process:
            return {"error": "Process not found"}
        
        risks = []
        risk_level = "low"
        suggestions = []
        
        # Check deadline risks
        deadline_status = deadline_awareness.calculate_deadline_status(
            process.prazo_final,
            alert_window_days=7
        )
        
        if deadline_status["status"] == "overdue":
            days_overdue = abs(deadline_status.get("days_until", 0))
            risks.append({
                "type": "deadline_overdue",
                "severity": "high",
                "message": f"Prazo vencido há {days_overdue} dia(s)",
                "field": "prazo_final",
                "suggestion": "Revisar urgência e tomar medidas corretivas"
            })
            risk_level = "high"
        
        elif deadline_status["status"] == "upcoming":
            days_until = deadline_status.get("days_until", 0)
            if days_until <= 3:
                risks.append({
                    "type": "deadline_imminent",
                    "severity": "medium",
                    "message": f"Prazo vence em {days_until} dia(s)",
                    "field": "prazo_final",
                    "suggestion": "Ação imediata recomendada"
                })
                risk_level = "medium" if risk_level == "low" else risk_level
        
        # Check missing critical information
        if not process.processo_adm_1doc and not process.processo_judicial:
            risks.append({
                "type": "missing_identifier",
                "severity": "high",
                "message": "Processo sem identificador (ADM ou Judicial)",
                "field": "identifiers",
                "suggestion": "Adicionar PROCESSO ADM 1DOC ou PROCESSO JUDICIAL"
            })
            risk_level = "high"
        
        if not process.partes:
            risks.append({
                "type": "missing_parties",
                "severity": "medium",
                "message": "Informação de partes ausente",
                "field": "partes",
                "suggestion": "Completar informação de partes envolvidas"
            })
            if risk_level == "low":
                risk_level = "medium"
        
        if not process.tema_observacoes:
            risks.append({
                "type": "missing_theme",
                "severity": "low",
                "message": "Tema/observações ausente",
                "field": "tema_observacoes",
                "suggestion": "Adicionar tema e observações relevantes"
            })
        
        # Check data consistency
        if process.prazo_final and process.data_realizacao_ato:
            # Simple check: if ato was performed, check if it's after deadline
            try:
                prazo_date = deadline_awareness.parse_prazo_final(process.prazo_final)
                if prazo_date:
                    # Parse data_realizacao_ato (DD/MM/YYYY)
                    parts = process.data_realizacao_ato.split('/')
                    if len(parts) == 3:
                        ato_date = date(int(parts[2]), int(parts[1]), int(parts[0]))
                        if ato_date > prazo_date:
                            risks.append({
                                "type": "late_action",
                                "severity": "medium",
                                "message": "Ato realizado após o prazo final",
                                "field": "data_realizacao_ato",
                                "suggestion": "Verificar se houve prorrogação ou justificativa"
                            })
            except:
                pass
        
        # Generate overall suggestion
        if risks:
            high_risks = [r for r in risks if r["severity"] == "high"]
            if high_risks:
                suggestions.append("Atenção: Existem riscos críticos que requerem ação imediata")
            else:
                suggestions.append("Revisar itens sinalizados para garantir completude")
        
        return {
            "process_id": process_id,
            "risk_level": risk_level,
            "total_risks": len(risks),
            "risks": risks,
            "suggestions": suggestions,
            "requires_attention": risk_level in ("high", "medium")
        }
    
    @staticmethod
    def get_process_insights(
        db: Session,
        process_id: int,
        include_summary: bool = True,
        include_prioritization: bool = True,
        include_risks: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive AI insights for a process.
        
        Args:
            db: Database session
            process_id: Process ID
            include_summary: Include observation summaries
            include_prioritization: Include prioritization suggestions
            include_risks: Include risk flags
            
        Returns:
            Dictionary with all requested insights
        """
        process = db.query(models.Process).filter(
            models.Process.id == process_id
        ).first()
        
        if not process:
            return {"error": "Process not found"}
        
        insights = {
            "process_id": process_id,
            "processo_adm_1doc": process.processo_adm_1doc,
            "processo_judicial": process.processo_judicial,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        if include_prioritization:
            insights["prioritization"] = AIInsightsService.suggest_prioritization(
                db, process_id
            )
        
        if include_summary:
            insights["summaries"] = {
                "tema_observacoes": AIInsightsService.summarize_observations(
                    process.tema_observacoes
                ),
                "partes": AIInsightsService.summarize_observations(
                    process.partes
                )
            }
        
        if include_risks:
            insights["risks"] = AIInsightsService.flag_potential_risks(
                db, process_id
            )
        
        return insights

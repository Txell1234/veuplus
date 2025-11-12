#!/usr/bin/env python3
"""
VeuPlus Test Suite - Suite de tests automatitzats
Tests E2E, API smoke tests, i integració de widgets
"""

import pytest
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List
import requests
from fastapi.testclient import TestClient

# Afegir el directori backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from server import app
    from api.convhi_agents import router as agents_router
    from api.convhi_widgets import router as widgets_router
    from api.convhi_batch_calling import router as batch_router
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Configuració de tests
TEST_CONFIG = {
    "base_url": "http://localhost:8080",
    "test_agent_id": "test_agent_001",
    "test_widget_id": "test_widget_001",
    "test_batch_id": "test_batch_001",
    "timeout": 30
}

class VeuPlusTestSuite:
    def __init__(self):
        self.client = TestClient(app)
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", duration: float = 0):
        """Registrar resultat de test"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if not success:
            self.failed_tests.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
    
    async def test_api_health(self) -> bool:
        """Test: API Health Check"""
        start_time = datetime.now()
        
        try:
            response = self.client.get("/api/health")
            duration = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.log_test("API Health Check", True, "API funcionant correctament", duration)
                    return True
            
            self.log_test("API Health Check", False, f"Status code: {response.status_code}", duration)
            return False
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("API Health Check", False, f"Error: {str(e)}", duration)
            return False
    
    async def test_convhi_agents_crud(self) -> bool:
        """Test: CRUD d'agents ConvHi"""
        start_time = datetime.now()
        
        try:
            # Test crear agent
            agent_data = {
                "id": TEST_CONFIG["test_agent_id"],
                "name": "Test Agent",
                "description": "Agent de prova per tests",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini",
                "voice_system": "edge-tts",
                "voice_id": "en-US-AriaNeural",
                "language": "ca"
            }
            
            response = self.client.post("/api/convhi/agents", json=agent_data)
            if response.status_code not in [200, 201]:
                self.log_test("ConvHi Agents CRUD", False, f"Error creant agent: {response.status_code}")
                return False
            
            # Test obtenir agent
            response = self.client.get(f"/api/convhi/agents/{TEST_CONFIG['test_agent_id']}")
            if response.status_code != 200:
                self.log_test("ConvHi Agents CRUD", False, f"Error obtenint agent: {response.status_code}")
                return False
            
            # Test actualitzar agent
            agent_data["name"] = "Test Agent Updated"
            response = self.client.put(f"/api/convhi/agents/{TEST_CONFIG['test_agent_id']}", json=agent_data)
            if response.status_code != 200:
                self.log_test("ConvHi Agents CRUD", False, f"Error actualitzant agent: {response.status_code}")
                return False
            
            # Test eliminar agent
            response = self.client.delete(f"/api/convhi/agents/{TEST_CONFIG['test_agent_id']}")
            if response.status_code != 200:
                self.log_test("ConvHi Agents CRUD", False, f"Error eliminant agent: {response.status_code}")
                return False
            
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("ConvHi Agents CRUD", True, "CRUD d'agents funcionant", duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("ConvHi Agents CRUD", False, f"Error: {str(e)}", duration)
            return False
    
    async def test_widget_system(self) -> bool:
        """Test: Sistema de widgets"""
        start_time = datetime.now()
        
        try:
            # Test crear configuració de widget
            widget_config = {
                "agent_id": TEST_CONFIG["test_agent_id"],
                "variant": "compact",
                "mode": "voice_only",
                "primary_color": "#3B82F6",
                "secondary_color": "#1E40AF",
                "action_text": "Test Widget",
                "start_call_text": "Start Test",
                "end_call_text": "End Test",
                "feedback_enabled": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            response = self.client.post("/api/convhi/widgets/config", json=widget_config)
            if response.status_code not in [200, 201]:
                self.log_test("Widget System", False, f"Error creant widget: {response.status_code}")
                return False
            
            # Test generar codi d'integració
            embed_request = {
                "agent_id": TEST_CONFIG["test_agent_id"],
                "config": widget_config,
                "domain": "localhost"
            }
            
            response = self.client.post("/api/convhi/widgets/embed", json=embed_request)
            if response.status_code != 200:
                self.log_test("Widget System", False, f"Error generant codi: {response.status_code}")
                return False
            
            embed_data = response.json()
            if not embed_data.get("success") or not embed_data.get("embed_code"):
                self.log_test("Widget System", False, "Codi d'integració no generat")
                return False
            
            # Test obtenir configuració
            response = self.client.get(f"/api/convhi/widgets/config/{TEST_CONFIG['test_agent_id']}")
            if response.status_code != 200:
                self.log_test("Widget System", False, f"Error obtenint configuració: {response.status_code}")
                return False
            
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Widget System", True, "Sistema de widgets funcionant", duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Widget System", False, f"Error: {str(e)}", duration)
            return False
    
    async def test_batch_calling_system(self) -> bool:
        """Test: Sistema de trucades massives"""
        start_time = datetime.now()
        
        try:
            # Test crear batch call
            batch_request = {
                "agent_id": TEST_CONFIG["test_agent_id"],
                "batch_name": "Test Batch",
                "description": "Batch de prova per tests",
                "max_concurrent_calls": 3,
                "retry_attempts": 1,
                "retry_delay_seconds": 30,
                "dynamic_variables": {},
                "call_settings": {}
            }
            
            test_records = [
                {
                    "phone_number": "+34123456789",
                    "name": "Test User 1",
                    "variables": {"test": "value1"}
                },
                {
                    "phone_number": "+34987654321",
                    "name": "Test User 2",
                    "variables": {"test": "value2"}
                }
            ]
            
            response = self.client.post("/api/convhi/batch-calling/create", json=batch_request)
            if response.status_code not in [200, 201]:
                self.log_test("Batch Calling System", False, f"Error creant batch: {response.status_code}")
                return False
            
            batch_data = response.json()
            if not batch_data.get("success"):
                self.log_test("Batch Calling System", False, "Batch no creat correctament")
                return False
            
            batch_id = batch_data.get("batch_id")
            
            # Test obtenir progrés
            response = self.client.get(f"/api/convhi/batch-calling/progress/{batch_id}")
            if response.status_code != 200:
                self.log_test("Batch Calling System", False, f"Error obtenint progrés: {response.status_code}")
                return False
            
            # Test llistar batches
            response = self.client.get("/api/convhi/batch-calling/batches")
            if response.status_code != 200:
                self.log_test("Batch Calling System", False, f"Error llistant batches: {response.status_code}")
                return False
            
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Batch Calling System", True, "Sistema de trucades massives funcionant", duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Batch Calling System", False, f"Error: {str(e)}", duration)
            return False
    
    async def test_widget_integration(self) -> bool:
        """Test: Integració de widget en pàgina web"""
        start_time = datetime.now()
        
        try:
            # Test servir arxiu JavaScript del widget
            response = self.client.get("/static/convhi-widget.js")
            if response.status_code != 200:
                self.log_test("Widget Integration", False, f"Error servint widget JS: {response.status_code}")
                return False
            
            # Verificar que el contingut és JavaScript vàlid
            content = response.text
            if "ConvHiWidget" not in content or "customElements" not in content:
                self.log_test("Widget Integration", False, "Contingut del widget no vàlid")
                return False
            
            # Test preview del widget
            response = self.client.get(f"/api/convhi/widgets/preview/{TEST_CONFIG['test_agent_id']}")
            if response.status_code != 200:
                self.log_test("Widget Integration", False, f"Error obtenint preview: {response.status_code}")
                return False
            
            preview_data = response.json()
            if not preview_data.get("success") or not preview_data.get("preview_html"):
                self.log_test("Widget Integration", False, "Preview no generat")
                return False
            
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Widget Integration", True, "Integració de widget funcionant", duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Widget Integration", False, f"Error: {str(e)}", duration)
            return False
    
    async def test_knowledge_system(self) -> bool:
        """Test: Sistema de coneixement i RAG"""
        start_time = datetime.now()
        
        try:
            # Test crear element de coneixement
            knowledge_data = {
                "agent_id": TEST_CONFIG["test_agent_id"],
                "title": "Test Knowledge",
                "content": "Això és un test del sistema de coneixement",
                "content_type": "text",
                "source_type": "manual"
            }
            
            response = self.client.post("/api/convhi/knowledge/items", json=knowledge_data)
            if response.status_code not in [200, 201]:
                self.log_test("Knowledge System", False, f"Error creant coneixement: {response.status_code}")
                return False
            
            # Test obtenir coneixement de l'agent
            response = self.client.get(f"/api/convhi/knowledge/agent/{TEST_CONFIG['test_agent_id']}")
            if response.status_code != 200:
                self.log_test("Knowledge System", False, f"Error obtenint coneixement: {response.status_code}")
                return False
            
            knowledge_response = response.json()
            if not knowledge_response.get("success"):
                self.log_test("Knowledge System", False, "Coneixement no obtingut")
                return False
            
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Knowledge System", True, "Sistema de coneixement funcionant", duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Knowledge System", False, f"Error: {str(e)}", duration)
            return False
    
    async def test_analytics_system(self) -> bool:
        """Test: Sistema d'analytics"""
        start_time = datetime.now()
        
        try:
            # Test obtenir analytics
            response = self.client.get("/api/convhi/analytics")
            if response.status_code != 200:
                self.log_test("Analytics System", False, f"Error obtenint analytics: {response.status_code}")
                return False
            
            analytics_data = response.json()
            if not analytics_data.get("success"):
                self.log_test("Analytics System", False, "Analytics no obtinguts")
                return False
            
            # Verificar estructura de dades
            required_fields = ["total_conversations", "total_agents", "success_rate"]
            for field in required_fields:
                if field not in analytics_data:
                    self.log_test("Analytics System", False, f"Camp {field} mancant")
                    return False
            
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Analytics System", True, "Sistema d'analytics funcionant", duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Analytics System", False, f"Error: {str(e)}", duration)
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Executar tots els tests"""
        print("🚀 Iniciant VeuPlus Test Suite...")
        print("=" * 50)
        
        test_methods = [
            self.test_api_health,
            self.test_convhi_agents_crud,
            self.test_widget_system,
            self.test_batch_calling_system,
            self.test_widget_integration,
            self.test_knowledge_system,
            self.test_analytics_system
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                result = await test_method()
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ ERROR inesperat en {test_method.__name__}: {str(e)}")
        
        print("=" * 50)
        print(f"📊 Resum de tests: {passed_tests}/{total_tests} passats")
        
        if self.failed_tests:
            print("\n❌ Tests fallits:")
            for test in self.failed_tests:
                print(f"  - {test['test_name']}: {test['message']}")
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n🎯 Taxa d'èxit: {success_rate:.1f}%")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": len(self.failed_tests),
            "success_rate": success_rate,
            "test_results": self.test_results,
            "failed_tests": self.failed_tests
        }

# Funció principal per executar tests
async def main():
    """Funció principal per executar la suite de tests"""
    test_suite = VeuPlusTestSuite()
    results = await test_suite.run_all_tests()
    
    # Guardar resultats en fitxer
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultats guardats en: {results_file}")
    
    # Retornar codi de sortida basat en resultats
    if results["success_rate"] >= 80:
        print("\n✅ Tests completats amb èxit!")
        return 0
    else:
        print("\n❌ Alguns tests han fallat!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)




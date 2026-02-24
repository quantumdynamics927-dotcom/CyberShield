import torch.nn as nn
import torch
from typing import Dict, List, Optional, Tuple, Any
import yaml
import json
from pathlib import Path

class SecurityAnalyzer(nn.Module):
    """Core security analysis engine for CyberLab Assistant."""
    
    def __init__(self, 
                 vocab_size: int,
                 embedding_dim: int = 768,
                 num_heads: int = 12,
                 num_layers: int = 6,
                 feedforward_dim: int = 3072,
                 max_sequence_length: int = 2048,
                 dropout: float = 0.1):
        super().__init__()
        
        self.embedding_dim = embedding_dim
        self.max_sequence_length = max_sequence_length
        
        # Token and position embeddings
        self.token_embedding = nn.Embedding(vocab_size, embedding_dim)
        self.position_embedding = nn.Embedding(max_sequence_length, embedding_dim)
        
        # Security feature extractors
        self.pattern_encoder = nn.Conv1d(embedding_dim, embedding_dim, kernel_size=3, padding=1)
        self.temporal_encoder = nn.LSTM(embedding_dim, embedding_dim // 2, num_layers=2, bidirectional=True)
        
        # Main transformer block
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=num_heads,
            dim_feedforward=feedforward_dim,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Task-specific heads
        self.threat_detector = nn.Linear(embedding_dim, 1)
        self.vulnerability_classifier = nn.Linear(embedding_dim, 4)  # Low, Medium, High, Critical
        self.command_generator = nn.Linear(embedding_dim, vocab_size)
        
        # Analysis cache
        self.analysis_cache = {}
        
    def forward(self, 
                input_ids: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """Forward pass with multiple security analysis outputs."""
        
        # Generate position ids
        position_ids = torch.arange(input_ids.shape[1], device=input_ids.device).unsqueeze(0)
        
        # Embeddings
        token_embeds = self.token_embedding(input_ids)
        pos_embeds = self.position_embedding(position_ids)
        embeddings = token_embeds + pos_embeds
        
        # Feature extraction
        pattern_features = self.pattern_encoder(embeddings.transpose(1, 2)).transpose(1, 2)
        temporal_features, _ = self.temporal_encoder(embeddings)
        
        # Combine features
        features = pattern_features + temporal_features
        
        # Transformer encoding
        if attention_mask is not None:
            padding_mask = attention_mask == 0
        else:
            padding_mask = None
            
        encoded = self.transformer(features, src_key_padding_mask=padding_mask)
        
        # Task-specific predictions
        threat_scores = self.threat_detector(encoded).squeeze(-1)
        vuln_classes = self.vulnerability_classifier(encoded)
        next_commands = self.command_generator(encoded)
        
        return {
            "threat_scores": threat_scores,
            "vulnerability_classes": vuln_classes,
            "command_predictions": next_commands,
            "encoded_features": encoded
        }
    
    def analyze_security_data(self, 
                            data: str,
                            data_type: str,
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze security-related data with caching."""
        
        # Generate cache key
        cache_key = f"{data_type}:{hash(data)}"
        if context:
            cache_key += f":{hash(str(context))}"
            
        # Check cache
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        # Process based on data type
        if data_type == "log":
            analysis = self._analyze_log_data(data, context)
        elif data_type == "scan":
            analysis = self._analyze_scan_data(data, context)
        elif data_type == "traffic":
            analysis = self._analyze_traffic_data(data, context)
        else:
            analysis = self._analyze_generic_data(data, context)
            
        # Cache results
        self.analysis_cache[cache_key] = analysis
        return analysis
    
    def _analyze_log_data(self, log_data: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze security log data."""
        findings = {
            "severity": "medium",  # placeholder
            "threats": [],
            "anomalies": [],
            "recommendations": []
        }
        return findings
    
    def _analyze_scan_data(self, scan_data: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze security scan results."""
        findings = {
            "vulnerabilities": [],
            "open_ports": [],
            "services": [],
            "recommendations": []
        }
        return findings
    
    def _analyze_traffic_data(self, traffic_data: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze network traffic data."""
        findings = {
            "patterns": [],
            "anomalies": [],
            "protocols": [],
            "recommendations": []
        }
        return findings
    
    def _analyze_generic_data(self, data: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze generic security-related data."""
        findings = {
            "insights": [],
            "risks": [],
            "recommendations": []
        }
        return findings
    
    def save_state(self, path: str):
        """Save model state and analysis cache."""
        state = {
            "model_state": self.state_dict(),
            "analysis_cache": self.analysis_cache
        }
        torch.save(state, path)
    
    def load_state(self, path: str):
        """Load model state and analysis cache."""
        state = torch.load(path)
        self.load_state_dict(state["model_state"])
        self.analysis_cache = state["analysis_cache"]
        
class IntentProcessor(nn.Module):
    """Process and understand user intents for security operations."""
    
    def __init__(self, vocab_size: int, embedding_dim: int = 768):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.intent_lstm = nn.LSTM(embedding_dim, embedding_dim, batch_first=True)
        self.intent_classifier = nn.Linear(embedding_dim, len(self.get_intent_types()))
        
    @staticmethod
    def get_intent_types() -> List[str]:
        """Get supported security operation intents."""
        return [
            "scan_network",
            "analyze_traffic",
            "check_vulnerabilities",
            "monitor_system",
            "investigate_logs",
            "configure_security",
            "generate_report"
        ]
        
    def forward(self, input_ids: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Process user input to determine security operation intent."""
        embeddings = self.embedding(input_ids)
        lstm_out, _ = self.intent_lstm(embeddings)
        intent_logits = self.intent_classifier(lstm_out[:, -1, :])
        return {
            "intent_logits": intent_logits,
            "encoded_input": lstm_out
        }

class CommandGenerator(nn.Module):
    """Generate secure system commands based on user intent."""
    
    def __init__(self, vocab_size: int, embedding_dim: int = 768):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.command_decoder = nn.TransformerDecoder(
            decoder_layer=nn.TransformerDecoderLayer(
                d_model=embedding_dim,
                nhead=8,
                batch_first=True
            ),
            num_layers=4
        )
        self.output_projection = nn.Linear(embedding_dim, vocab_size)
        
        # Command templates and security rules
        self.load_command_templates()
        
    def load_command_templates(self):
        """Load secure command templates and rules."""
        template_path = Path(__file__).parent / "config" / "command_templates.yaml"
        if template_path.exists():
            with open(template_path) as f:
                self.templates = yaml.safe_load(f)
        else:
            self.templates = {}
            
    def forward(self,
               encoded_intent: torch.Tensor,
               command_prefix: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Generate secure system commands based on understood intent."""
        if command_prefix is not None:
            prefix_embeddings = self.embedding(command_prefix)
            output = self.command_decoder(prefix_embeddings, encoded_intent)
        else:
            batch_size = encoded_intent.shape[0]
            start_token = torch.zeros((batch_size, 1), dtype=torch.long, device=encoded_intent.device)
            output = self.command_decoder(self.embedding(start_token), encoded_intent)
            
        return self.output_projection(output)
    
    def validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate generated command against security rules."""
        # TODO: Implement command validation
        return True, "Command validated"

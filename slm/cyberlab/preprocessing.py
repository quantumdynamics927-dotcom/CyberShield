from typing import List, Dict, Any, Optional
import torch
import numpy as np
from pathlib import Path
import yaml
import json

class SecurityLogParser:
    """Parser for various security tool outputs and log formats."""
    
    def __init__(self, patterns_file: Optional[str] = None):
        self.patterns = {}
        if patterns_file:
            self.load_patterns(patterns_file)
    
    def load_patterns(self, patterns_file: str):
        """Load log parsing patterns from a YAML file."""
        with open(patterns_file, 'r') as f:
            self.patterns = yaml.safe_load(f)
    
    def parse_nmap_output(self, content: str) -> Dict[str, Any]:
        """Parse Nmap scan output."""
        result = {
            "hosts": [],
            "ports": [],
            "services": [],
            "vulnerabilities": []
        }
        
        # TODO: Implement Nmap output parsing
        return result
    
    def parse_nikto_output(self, content: str) -> Dict[str, Any]:
        """Parse Nikto web server scanner output."""
        result = {
            "target": "",
            "findings": [],
            "vulnerabilities": []
        }
        
        # TODO: Implement Nikto output parsing
        return result
    
    def parse_wireshark_output(self, content: str) -> Dict[str, Any]:
        """Parse Wireshark/tcpdump output."""
        result = {
            "packets": [],
            "protocols": [],
            "conversations": []
        }
        
        # TODO: Implement Wireshark/tcpdump parsing
        return result

class TokenizerWrapper:
    """Wrapper for SentencePiece tokenizer with security-specific vocabulary."""
    
    def __init__(self, model_path: str):
        import sentencepiece as spm
        self.sp = spm.SentencePieceProcessor()
        self.sp.Load(model_path)
        
    @property
    def vocab_size(self) -> int:
        return self.sp.GetPieceSize()
        
    def encode(self, text: str) -> List[int]:
        """Encode text to token ids."""
        return self.sp.EncodeAsIds(text)
        
    def decode(self, ids: List[int]) -> str:
        """Decode token ids to text."""
        return self.sp.DecodeIds(ids)
        
    def train(self, input_file: str, model_prefix: str, vocab_size: int = 8000):
        """Train a new tokenizer model."""
        import sentencepiece as spm
        spm.SentencePieceTrainer.Train(
            f'--input={input_file} '
            f'--model_prefix={model_prefix} '
            f'--vocab_size={vocab_size} '
            '--character_coverage=1.0 '
            '--model_type=bpe '
            '--max_sentence_length=2048'
        )

class DataProcessor:
    """Process and prepare data for the SLM model."""
    
    def __init__(self, tokenizer: TokenizerWrapper, max_seq_length: int = 1024):
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length
        
    def prepare_batch(self, texts: List[str]) -> Dict[str, torch.Tensor]:
        """Prepare a batch of texts for the model."""
        # Tokenize all texts
        token_ids = [self.tokenizer.encode(text) for text in texts]
        
        # Pad sequences
        padded = self._pad_sequences(token_ids)
        
        # Create attention mask
        attention_mask = self._create_attention_mask(padded)
        
        return {
            'input_ids': torch.tensor(padded),
            'attention_mask': torch.tensor(attention_mask)
        }
    
    def _pad_sequences(self, sequences: List[List[int]]) -> List[List[int]]:
        """Pad sequences to max_seq_length."""
        padded = []
        for seq in sequences:
            if len(seq) > self.max_seq_length:
                padded.append(seq[:self.max_seq_length])
            else:
                padded.append(seq + [0] * (self.max_seq_length - len(seq)))
        return padded
    
    def _create_attention_mask(self, padded_sequences: List[List[int]]) -> List[List[int]]:
        """Create attention mask for padded sequences."""
        return [[1 if token != 0 else 0 for token in seq] for seq in padded_sequences]

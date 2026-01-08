"""
Task Extraction Services - LangChain Implementation

This package uses LangChain as the core framework for all AI operations:

Components:
- text_extractor.py: LangChain + OLLAMA for text extraction
- vision_extractor.py: LangChain + Gemini Vision for images
- audio_processor.py: Whisper + LangChain chains
- video_processor.py: moviepy + Whisper + LangChain
- document_processor.py: LangChain UnstructuredFileLoader + chains
- image_processor.py: LangChain multimodal
- deduplicator.py: LangChain + OLLAMA for merging

LangChain Features Used:
✅ Prompts (PromptTemplate, ChatPromptTemplate)
✅ LLMs (Ollama, ChatGoogleGenerativeAI)
✅ Output Parsers (PydanticOutputParser, JsonOutputParser)
✅ Chains (LCEL - LangChain Expression Language)
✅ Document Loaders (UnstructuredFileLoader)
✅ Multimodal (HumanMessage with images)
"""

# Lazy imports - only load when actually needed
# Commenting out to avoid loading heavy dependencies like Whisper
# from . import audio_processor
# from . import video_processor
# from . import document_processor
# from . import image_processor
# from . import text_extractor
# from . import vision_extractor
# from . import dedublicator

__all__ = [
    # 'audio_processor',
    # 'video_processor',
    # 'document_processor',
    # 'image_processor',
    # 'text_extractor',
    # 'vision_extractor',
    # 'dedublicator'
]
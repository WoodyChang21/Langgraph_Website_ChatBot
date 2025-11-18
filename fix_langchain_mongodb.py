#!/usr/bin/env python3
"""
Fix langchain-mongodb imports for LangChain 1.0+ compatibility.

This patches the bug where langchain-mongodb tries to import from langchain.retrievers
which doesn't exist in LangChain 1.0+. The imports have moved to langchain_classic.
"""
import site
from pathlib import Path

# Find langchain_mongodb package location
paths = [Path(p) / 'langchain_mongodb' for p in site.getsitepackages()]
paths.append(Path(site.getusersitepackages()) / 'langchain_mongodb')

langchain_path = next((p for p in paths if p.exists()), None)

if langchain_path:
    print(f"Found langchain_mongodb at: {langchain_path}")
    
    # Fix parent_document.py
    parent_doc = langchain_path / 'retrievers' / 'parent_document.py'
    if parent_doc.exists():
        content = parent_doc.read_text(encoding='utf-8')
        if 'from langchain.retrievers.parent_document_retriever' in content:
            content = content.replace(
                'from langchain.retrievers.parent_document_retriever import ParentDocumentRetriever',
                'from langchain_classic.retrievers.parent_document_retriever import ParentDocumentRetriever'
            )
            parent_doc.write_text(content, encoding='utf-8')
            print('✅ Fixed parent_document.py')
        else:
            print('ℹ️  parent_document.py already fixed or doesn\'t need fixing')
    
    # Fix self_querying.py
    self_query = langchain_path / 'retrievers' / 'self_querying.py'
    if self_query.exists():
        content = self_query.read_text(encoding='utf-8')
        original = content
        content = content.replace(
            'from langchain.retrievers.self_query.base import SelfQueryRetriever',
            'from langchain_classic.retrievers.self_query.base import SelfQueryRetriever'
        )
        content = content.replace(
            'from langchain.chains.query_constructor.schema import AttributeInfo',
            'from langchain_classic.chains.query_constructor.schema import AttributeInfo'
        )
        if content != original:
            self_query.write_text(content, encoding='utf-8')
            print('✅ Fixed self_querying.py')
        else:
            print('ℹ️  self_querying.py already fixed or doesn\'t need fixing')
else:
    print('⚠️  langchain_mongodb package not found')


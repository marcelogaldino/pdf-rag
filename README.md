# 📚 PDF RAG 

Este projeto implementa **três arquiteturas distintas de RAG (Retrieval-Augmented Generation)**, Naive RAG, Parent RAG e Rerank RAG

> Todas as abordagens foram usadas para um unico documento PDF, mas variam na estratégia de recuperação e construção da resposta.

---

## 🧠 O que é RAG?

RAG combina recuperação de informações (busca semântica com embeddings) com geração de texto (LLM como GPT), para responder perguntas com base em dados externos.

---

## 🔗 Tecnologias utilizadas

- 📘 [LangChain](https://www.langchain.com/)
- 🧠 OpenAI GPT (Chat + Embeddings)
- 💾 [ChromaDB](https://www.trychroma.com/) - vector store local
- 🔤 [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) - extração do PDF
- 🧱 RecursiveCharacterTextSplitter (chunking)

---

## ✅ Estruturas de RAG implementadas

### 1. 🧱 Naive RAG (simples)

> Recupera os `top-k` chunks com embeddings e envia diretamente ao LLM.

```mermaid
flowchart TD
    A[Pergunta do Usuário] --> B[Retriever (Top-k Chunks)]
    B --> C[LLM (GPT)]
    C --> D[Resposta Gerada]
```

✅ **Vantagens**: simples, rápido, fácil de implementar  
⚠️ **Limitações**: chunks isolados podem perder contexto

**Melhorias futuras**:
- Ajuste dinâmico de `k` com base na complexidade da pergunta
- Filtros por metadado (capítulo, tema)
- Prompt adaptativo conforme tipo de questão

---

### 2. 🧩 Parent RAG (com contexto estendido)

> Cada chunk pequeno aponta para um "documento pai" maior. Após buscar os chunks, recupera os pais para garantir contexto completo.

```mermaid
flowchart TD
    A[Pergunta do Usuário] --> B[Retriever (Chunks Pequenos)]
    B --> C[Mapeamento para Parent ID]
    C --> D[Recupera Texto Completo (Parent)]
    D --> E[LLM (GPT)]
    E --> F[Resposta Gerada]
```

✅ **Vantagens**: preserva contexto completo de seções grandes  
⚠️ **Limitações**: pode passar muito conteúdo irrelevante ao LLM

**Melhorias futuras**:
- Agrupar parents por similaridade semântica
- Truncamento automático por token máximo
- Cache por parent já usado

---

### 3. 🧠 Rerank RAG (relevância avaliada por LLM)

> Recupera muitos chunks (`top-15~20`), depois o LLM reordena com base em relevância para a pergunta. Os melhores são usados na resposta.

```mermaid
flowchart TD
    A[Pergunta do Usuário] --> B[Retriever (Top-20 Chunks)]
    B --> C[LLM Reranker (Avalia Relevância)]
    C --> D[Seleciona Top-N Chunks]
    D --> E[LLM (GPT)]
    E --> F[Resposta Gerada]
```

✅ **Vantagens**: melhora a precisão ao selecionar só os chunks realmente relevantes  
⚠️ **Limitações**: mais custo em chamadas ao LLM

**Melhorias futuras**:
- Substituir o reranker por um modelo local (ex: BGE-M3 ou Cohere ReRank)
- Otimização via batch para scoring paralelo
- Rerank com metadados (capítulo, personagem, local)

---

## 📊 Comparativo entre as abordagens

| Critério             | Naive RAG | Parent RAG | Rerank RAG |
|----------------------|-----------|------------|------------|
| Implementação        | ✅ Simples | ⚠️ Moderada | ⚠️ Complexa |
| Qualidade de contexto| ❌ Baixa   | ✅ Alta     | ✅ Alta     |
| Custo computacional  | ✅ Baixo   | ⚠️ Médio    | ❌ Alto     |
| Precisão nas respostas | ⚠️ Variável | ✅ Boa   | ✅ Ótima    |

---

## 🚀 Próximos passos (gerais)

- Interface Web
- Logging de perguntas e respostas
- Avaliação automática das respostas (score semântico + humano)
- Suporte a perguntas conversacionais (contexto contínuo)
- Comparador entre as 3 abordagens lado a lado

---

## 👤 Autor

Made with ♥ by Marcelo Galdino :wave: [Get in touch!](https://www.linkedin.com/in/marcelogaldino/)


## 📝 Licença

Este projeto é distribuído sob a licença MIT.
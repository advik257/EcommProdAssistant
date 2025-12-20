from ragas import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import LLMContextPrecisionWithoutReference,ResponseRelevancy
import grpc.experimental.aio as grpc_aio
grpc_aio.init_grpc_aio()
from prod_assistant.utils.model_loader import ModelLoader
import asyncio



model_loder = ModelLoader()


def evaluate_context_precision(query, response, retrieved_context):
    
    try:
        sample = SingleTurnSample(
            user_input=query,
            response=response,
            retrieved_contexts=retrieved_context,
        )

        async def main():
            llm = ModelLoader.load_llm()
            evaluator_llm = LangchainLLMWrapper(llm)
            context_precision = LLMContextPrecisionWithoutReference(llm=evaluator_llm)
            result = await context_precision.single_turn_ascore(sample)
            return result

        return asyncio.run(main())
    
    except Exception as e:
        return e



def evaluate_response_relevancy(query, response, retrieved_context):
    try:
        sample = SingleTurnSample(
            user_input=query,
            response=response,
            retrieved_contexts=retrieved_context,
        )

        async def main():
            llm = model_loder.load_llm()
            evaluator_llm = LangchainLLMWrapper(llm)
            embedding_model = model_loder.load_embeddings()
            evaluator_embeddings = LangchainEmbeddingsWrapper(embedding_model)
            scorer = ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings)
            result = await scorer.single_turn_ascore(sample)
            return result

        return asyncio.run(main())
    except Exception as e:
        return e


# def evaluate_retriever_hit_rate(self):
#     pass   
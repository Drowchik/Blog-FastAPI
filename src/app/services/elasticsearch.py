from elasticsearch import AsyncElasticsearch

from src.app.models import Post

class Search:
    def __init__(self) -> None:
        self.es = AsyncElasticsearch(hosts=["http://localhost:9200"])
        
    async def create_index(self):
        if not await self.es.indices.exists(index="blog_posts"):
            await self.es.indices.create(index="blog_posts", body={
                "mappings":{
                    "properties": {
                        "title": "text",
                        "description": "text",
                    }
                }
            })
        
    async def index_post(self, post: Post):
        await self.es.index(index="blog_posts", id=post.id, body= {
            "title": post.title,
            "description": post.description},
        )
    
    async def search_post(self, query: str):
        response = await self.es.search(index="blog_posts", body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "description"]
                }
            }
        })
        return response
    
    async def close(self):
        await self.es.close()
        
es = Search()

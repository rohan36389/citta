import logging
from typing import Dict, Any, List, Set, Optional
from memory_store import get_memory_store, EnterpriseMemory

logger = logging.getLogger(__name__)

class MemoryIndex:
    def __init__(self):
        self.store = get_memory_store()
        self.by_user: Dict[str, Set[str]] = {}
        self.by_org: Dict[str, Set[str]] = {}
        self.by_entity: Dict[str, Set[str]] = {}
        self.by_type: Dict[str, Set[str]] = {}
        self.reindex()

    def reindex(self):
        self.by_user.clear()
        self.by_org.clear()
        self.by_entity.clear()
        self.by_type.clear()

        for mem_id, mem in self.store.memories.items():
            if mem.is_deleted:
                continue

            self.by_user.setdefault(mem.owner_user_id, set()).add(mem_id)
            self.by_org.setdefault(mem.organization_id, set()).add(mem_id)
            self.by_type.setdefault(mem.type, set()).add(mem_id)

            if mem.entity_id:
                self.by_entity.setdefault(mem.entity_id, set()).add(mem_id)

    def index_memory(self, mem: EnterpriseMemory):
        mem_id = mem.memory_id
        self.by_user.setdefault(mem.owner_user_id, set()).add(mem_id)
        self.by_org.setdefault(mem.organization_id, set()).add(mem_id)
        self.by_type.setdefault(mem.type, set()).add(mem_id)
        if mem.entity_id:
            self.by_entity.setdefault(mem.entity_id, set()).add(mem_id)

    def search(
        self,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        memory_type: Optional[str] = None
    ) -> List[EnterpriseMemory]:
        candidate_ids = set(self.store.memories.keys())

        if user_id and user_id in self.by_user:
            candidate_ids.intersection_update(self.by_user[user_id])
        if org_id and org_id in self.by_org:
            candidate_ids.intersection_update(self.by_org[org_id])
        if entity_id and entity_id in self.by_entity:
            candidate_ids.intersection_update(self.by_entity[entity_id])
        if memory_type and memory_type in self.by_type:
            candidate_ids.intersection_update(self.by_type[memory_type])

        results = []
        for mem_id in candidate_ids:
            mem = self.store.get_memory(mem_id)
            if mem and not mem.is_deleted and not mem.is_archived:
                results.append(mem)

        return results

_memory_index_instance = None

def get_memory_index() -> MemoryIndex:
    global _memory_index_instance
    if _memory_index_instance is None:
        _memory_index_instance = MemoryIndex()
    return _memory_index_instance

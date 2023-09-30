from jarvis_backend.app.workers.base import SimpleWorker


class CacheWorker(SimpleWorker):
    def __init__(self):
        super().__init__(5)

    def task(self):
        print('halo')
        # db_context = db_context_depends()
        # marketplace_id = 2
        # with db_context.session() as session, session.begin():
        #     category_service = JDBServiceFactory.create_category_service(session)
        #     id_to_category = category_service.find_all_in_marketplace(marketplace_id)
        # category_to_niche = {}
        # with db_context.session() as session, session.begin():
        #     niche_service = JDBServiceFactory.create_niche_service(session)
        #     for category_id in id_to_category:
        #         category_to_niche[category_id] = list(niche_service.find_all_in_category(category_id).keys())

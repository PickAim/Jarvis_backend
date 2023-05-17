from app.calc.calculation import CalculationController
from sessions.controllers import JarvisSessionController, RequestHandler

calculation_controller: CalculationController = CalculationController()
session_controller: JarvisSessionController = JarvisSessionController()
request_handler: RequestHandler = RequestHandler()

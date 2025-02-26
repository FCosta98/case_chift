from fastapi import FastAPI
from controller import contact_controller, facture_controller

app = FastAPI(
    swagger_ui_parameters={"persistAuthorization": True}
)

# Register the routers
app.include_router(contact_controller.contact_router)
app.include_router(facture_controller.facture_router)


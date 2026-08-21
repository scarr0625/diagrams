from fastapi import FastAPI, Request
from jose import jwt


app = FastAPI()


@app.post("/agent")
async def agent(request:Request):

    token = request.headers["Authorization"]

    jwt_token = token.replace(
        "Bearer ",
        ""
    )

    user = jwt.decode(
        jwt_token,
        options={
          "verify_signature":False
        }
    )


    user_context = {
        "email":user["email"],
        "role":user.get("role")
    }


    return {
        "message":"Authenticated",
        "user":user_context
    }
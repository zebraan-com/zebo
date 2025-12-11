#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from zebo.crews.poem_crew.poem_crew import PoemCrew

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="CrewAI API", version="1.0")


class PoemState(BaseModel):
    sentence_count: int = 1
    poem: str = ""


class PoemFlow(Flow[PoemState]):

    def get_poem(self):
        return self.state.poem
    
    @start()
    def generate_sentence_count(self):
        print("Generating sentence count")
        self.state.sentence_count = randint(1, 5)

    @listen(generate_sentence_count)
    def generate_poem(self):
        print("Generating poem")
        result = (
            PoemCrew()
            .crew()
            .kickoff(inputs={"sentence_count": self.state.sentence_count})
        )

        print("Poem generated", result.raw)
        self.state.poem = result.raw

    @listen(generate_poem)
    def save_poem(self):
        print("Saving poem")
        with open("poem.txt", "w") as f:
            f.write(self.state.poem)
            
        return self.state.poem


def kickoff():
    poem_flow = PoemFlow()
    output = poem_flow.kickoff()
    print("Poem generated: ", output)


def plot():
    poem_flow = PoemFlow()
    poem_flow.plot()
    
class RunRequest(BaseModel):
    sentence_count: int | None = None

@app.post("/run")
async def run_crewai_task(req: RunRequest):
    try:
        flow = PoemFlow()

        # If sentence_count provided, set state and run the remaining steps manually.
        if req.sentence_count is not None:
            flow.state.sentence_count = req.sentence_count
            flow.generate_poem()
            poem = flow.save_poem()
        else:
            # Otherwise, run the whole flow (random sentence_count 1-5)
            poem = flow.kickoff()

        return {
            "sentence_count": flow.state.sentence_count,
            "poem": poem,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "CrewAI API is up and running!"}


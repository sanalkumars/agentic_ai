from agents import build_Reader_Agent , build_Search_Agent,writer_Chain,critic_Chain


def run_research_pipeline( topic :str ) -> dict:

    state = {}

    # step-1 search agent working/running

    print("\n" + "="*50)
    print("Step 1 - Search Agent is working....")
    print("="*50)

    search_Agent = build_Search_Agent()
    search_result = search_Agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"Find recent and reliable information about :{topic}"
            }
        ]
    })
    # now we will store the "AIMessage from the search_result"
    state[ "search_result" ] = search_result['messages'][-1].content

    print("\n Search Result",state["search_result"])

    # step-2 Running/Working Reader Agent
    print("\n" + "="*50)
    print("Step 2 - Reader Agent is Scraping ....")
    print("="*50)

    reader_agent = build_Reader_Agent()
    reader_result = reader_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Based on the following search result about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Result:\n{state['search_result'][:800]}"
                ),
            }
        ]
    })
    # now we store the result from scrape in to the state
    state["scrape_result"] = reader_result['messages'][-1].content

    print("\n Scraped Content\n",state["scrape_result"])

    # step-3 ----- writer chain ------
    print("\n" + "="*50)
    print("Step 3 - Writer  is drafting the report ....")
    print("="*50)

    # we combaine the search and scrape results
    research_result =(
        f"SEARCH RESULTS: \n {state['search_result']} \n\n"
        f"DETAILED SCRAPED CONTENTS: \n {state['scrape_result']}"
    )

    # invoking the writer chain for creating the report, and we save it in the state["report"]
    state["report"]=writer_Chain.invoke({
        "topic" : topic,
        "research" : research_result
    })

    print("\n\n Final Report \n\n")
    print(state["report"])

    # invoking the critic_Chain for creating the critic report  and save it in state["critic_report"]
    
    # step-4 ----- Critic Chain  ------
    print("\n" + "="*50)
    print("Step 4 - Writer  is drafting the report ....")
    print("="*50)

    state["feedback"] = critic_Chain.invoke({ 
        "report" : state["report"]
        })
    print("\n\n  Critcs Report \n\n")
    print(state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\n Enter a research topic :")
    run_research_pipeline(topic=topic)
    

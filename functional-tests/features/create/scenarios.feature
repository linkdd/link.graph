Feature: Create
    In order to create node and links
    As users
    We'll run the corresponding request

    Scenario: Riak and IPython
        Given I have a graph with:
        """
        parallel_backend=mapreduce+ipython:///riak/ipython?store_uri=kvstore%2Briak%3A%2F%2Flocalhost%3A8087%2Fdefault%2Friak_ipython%3Fprotocol%3Dpbc
        nodes_storage=kvstore+riak://localhost:8087/nodes/default
        relationships_storage=kvstore+riak://localhost:8087/relationships/default
        """
        Then I can execute the request "features/create/request.txt"
        And I have the same result as "features/create/result.json"

    Scenario: Riak and multiprocessing
        Given I have a graph with:
        """
        parallel_backend=mapreduce+multiprocessing:///riak/proc?store_uri=kvstore%2Briak%3A%2F%2Flocalhost%3A8087%2Fdefault%2Friak_proc%3Fprotocol%3Dpbc
        nodes_storage=kvstore+riak://localhost:8087/nodes/default
        relationships_storage=kvstore+riak://localhost:8087/relationships/default
        """
        Then I can execute the request "features/create/request.txt"
        And I have the same result as "features/create/result.json"

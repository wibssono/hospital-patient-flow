import patient_flow_generator

class Theater(object):
    def __init__(self, env, num_cashiers):
        self.env = env
        self.cashier = simpy.Resource(env, num_cashiers)

    def purchase_ticket(self, moviegoer):
        yield self.env.timeout(random.randint(1, 3))

    def go_to_movies(env, moviegoer, theater):
    # Moviegoer arrives at the theater
        arrival_time = env.now

    def go_to_movies(env, moviegoer, theater):
    # Moviegoer arrives at the theater
        arrival_time = env.now

        with theater.cashier.request() as request:
            yield request
            yield env.process(theater.purchase_ticket(moviegoer))
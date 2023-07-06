#Linux side recieving recorded commands 
import Pyro4


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")

class RecievedActions():

    def __init__(self):
        self.humanActions = {}
        self.actionNumber = 0

    def recieve_data(self, humanPickle):
        self.humanActions[self.actionNumber] = humanPickle
        self.actionNumber += 1
        print("I MADE IT")

if __name__ == "__main__":
    Pyro4.Daemon.serveSimple(
            {
                RecievedActions: "example.recievedHuman"
            },
            host = '134.173.38.19', port = 9092,
            ns = True)



class iDict:
    def __init__(self) -> None:

        #print("@iDict.__init__()")
        self.i = 0
        self.accumulator = 0
        self.dict = {}

    def add_entry(self, entry):

        #print(f"@iDict.add_entry(entry={entry})")

        #print(self.dict)
        self.i += 1
        self.accumulator += entry

        # add +1 to entry i in i_dict or create entry i in i_dict with value 1 if it doesn't exist
        self.dict[entry] = self.dict.get(entry, 0) + 1

        #print(self.dict)

    def get_average(self):
        return self.accumulator/self.i


    def get_dict(self):

        #print("@iDict.get_dict()")

        #print(self.dict)

         # soft i_dict from lower to higher by the key value
        self.dict = {k: v for k, v in sorted(self.dict.items(), key=lambda item: item[0])}

        #print(self.dict)
        

        return self.dict
    
    def get_results(self):
        return self.get_dict(), self.get_average()
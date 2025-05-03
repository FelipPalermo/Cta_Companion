from pymongo.mongo_client import MongoClient
from datetime import datetime, timedelta
from hash import static_hash
from typing import Union
import os

mongo_token = os.getenv("MONGODB_TOKEN")

Uri = "mongodb+srv://admin:admin@cluster0.mn86c6t.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
Client = MongoClient(Uri)["CTA_PLAYERS"]
Client_Options = MongoClient(Uri)["CTA_OPTIONS"]

def index_deleted_players() : 

    Client["Deleted_Players"].create_index(
    [("createdAt", 1)],
    expireAfterSeconds=60)

class Mongo :

    @staticmethod
    def check_exist(id: str) -> bool:
        return Client["Players"].find_one({"_id": id}) is not None


    @staticmethod
    def register(id, name : str) -> None : 
        
        id = static_hash(id)

        if Mongo.check_exist(id)  == False : 
            Client["Players"].insert_one({
                "_id": id,
                "name" : name,
                "Privacy policys" : True,
                "Loggin_on_call" :[], 
                "Presence" : [],
                "Absence" : []
            })
        else : 
            pass
    
    @staticmethod
    def event_log(guild, start, end: str) -> None : 

        guild = static_hash(guild)

        Client["Events"].insert_one({
            "Guild" : guild, 
            "start_date" : start,
            "end_date" : end,
            "Players" : []
        })


    @staticmethod
    def insert_logged_in(id : str) -> None :

        id = static_hash(id)
        now = datetime.now().strftime("")

        if Mongo.check_exist(id) :            
            Client["Players"].update_one({"_id" : id},
                {"$push" : {"Loggin_on_call" : now}})
        else : 
            pass

    @staticmethod
    def insert_presence(id : str) -> None : 
        id = static_hash(id)
        now = datetime.now().strftime("%H:%M %d-%m-%y")

        if Mongo.check_exist(id) : 
            Client["Players"].update_one({"_id" : id},
                {"$push" : {"Presence" : now}})
        else : 
            pass 

    @staticmethod
    def insert_absence(id : str) -> None : 
        id = static_hash(id)
        now = datetime.now().strftime("%d-%m-%y %H:%M")

        if Mongo.check_exist(id) : 
            Client["Players"].update_one({"_id" : id}, 
                {"$push" : {"Absence" : now}})

    @staticmethod
    def delete_own_documment(id : str) -> None : 

        id = static_hash(id) 

        if Mongo.check_exist(id) : 
            result = Client["Players"].delete_one({"_id" : id})
            if result == 1 : 
                print("Documento foi deletado com sucesso!")

                Client["Deleted_Players"].insert_one({"_id" : id,
                        "CreatedAt" : datetime.now(datetime.timezone.utc)}) 

            else : 
                print("Houve um erro ao deletar documento de personagem!")

        else : 
            pass 


    @staticmethod
    def show_Absence() -> list : 
        collection = Client["Players"]

        # Busca jogadores que tenham pelo menos uma falta
        cursor = collection.find(
            {"Absence": {"$exists": True, "$ne": []}},  # `Not_on_call` existe e não é lista vazia
            {"_id": 0, "name": 1, "Absence": 1}          # Projeta só o nome e Not_on_call
        )

        # Organiza por número de faltas (decrescente)
        jogadores = sorted(
            [{"nome": doc["name"], "faltas": len(doc["Absence"]), "dias_faltados" : str(doc["Absence"])} for doc in cursor],
            key=lambda x: x["faltas"],
            reverse=True
        )

        resultado = ""
        for jogador in jogadores:
            resultado += f"Nome : {jogador['nome'].capitalize()}\nFaltas : {jogador['faltas']}\nDias faltados : {jogador["dias_faltados"]}\n-----\n"

        return resultado


# ------ /// Server methods /// ------

    @staticmethod
    def check_exist_sv(id: str) -> bool:
        return Client["Server_Options"].find_one({"_id": id}) is not None


    @staticmethod
    def create_server(guild_id) : 

        guild_id = static_hash(guild_id)

        if not Mongo.check_exist_sv(guild_id) : 

            Client["Server_Options"].insert_one({
                "_id" : guild_id,
                "cta_role" : "cta",
                "cta_manager_role" : "CTA MANAGER",
                "voice_channel_name" : "cta room",
                "voice_log_name" : "cta-voice-log",
                "commands_name" : "cta-commands"
            })
        else : 
            print("Servidor está tentando ser registrado novamente")


    @staticmethod
    def change_voice_channel_name(guild_id, name : str) -> None : 

        guild_id = static_hash(guild_id)

        if Mongo.check_exist_sv(guild_id) : 
            Client["Server_Options"].update_one(
                {"_id" : guild_id}, 
                {"$set" : {"voice_channel_name" : name}}
            )

        else : 
            return 

    @staticmethod
    def change_voice_log_name(guild_id, name : str) -> None : 

        guild_id = static_hash(guild_id)

        if Mongo.check_exist_sv(guild_id) : 
            Client["Server_Options"].update_one(
                {"_id" : guild_id}, 
                {"$set" : {"voice_log_name" : name}}
            )

        else : 
            return 

    @staticmethod
    def change_command_name(guild_id, name : str) -> None : 

        guild_id = static_hash(guild_id)

        if Mongo.check_exist_sv(guild_id) : 
            Client["Server_Options"].update_one(
                {"_id" : guild_id}, 
                {"$set" : {"commands_name" : name}}
            )

        else : 
            return 

    @staticmethod
    def change_cta_role_name(guild_id, name : str) -> None : 

        guild_id = static_hash(guild_id)

        if Mongo.check_exist_sv(guild_id) : 
            Client["Server_Options"].update_one(
                {"_id" : guild_id}, 
                {"$set" : {"cta_role" : name}}
            )

        else : 
            return 

    @staticmethod
    def change_cta_manager_role_name(guild_id, name : str) -> None : 

        guild_id = static_hash(guild_id)

        if Mongo.check_exist_sv(guild_id) : 
            Client["Server_Options"].update_one(
                {"_id" : guild_id}, 
                {"$set" : {"cta_manager_role" : name}}
            )

        else : 
            return 

    @staticmethod
    def get_server_properties(guild_id) : 

        guild_id = static_hash(guild_id) 

        if Mongo.check_exist_sv(guild_id) :  
            print("existe")
            server = Client["Server_Options"].find_one({"_id": guild_id})
            return server
        
        else : 
            return None 

        

        

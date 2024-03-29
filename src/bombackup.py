import logging
import toml

def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='bombackup.log', encoding='utf-8', level=logging.DEBUG)
    logger.debug('This message should go to the log file')
    logger.info('So should this')
    logger.warning('And this, too')
    logger.error('And non-ASCII stuff, too, like Øresund and Malmö')
    file=open("config.toml","w")
    data_dict = {
        "devices" : {
            "name" : "Device-name",
            "ip" : "Device-IP",
            
            "mailTo" : "Your-email-address",
            "path" : "/path/to/folder",
            
        }
    }
            
            
    print(tomldata)
    print("Hello, World!")
    

if __name__ == "__main__":
    main()
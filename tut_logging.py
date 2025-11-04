import logging

def condition1():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s)"
    )

    # Example logs
    logging.debug("This is a debug message")
    logging.info("Application started successfully")
    logging.warning("Low disk space")
    logging.error("File not found")
    logging.critical("System crash!")

def condition2():
    logging.basicConfig(
        filename='app.log',
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("This message will go into app.log")

if __name__ == "__main__":
    condition2()
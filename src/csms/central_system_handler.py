import asyncio
import logging

from fastapi import HTTPException, status

from src.csms.charge_point_handler import ChargePointHandler


class CentralSystem:
    def __init__(self):
        self._chargers = {}

    def register_charger(self, cp: ChargePointHandler):
        """ Register a new ChargePoint at the CSMS. The function returns a
        queue.  The CSMS will put a message on the queue if the CSMS wants to
        close the connection.
        """
        queue = asyncio.Queue(maxsize=1)

        # Store a reference to the task, so we can cancel it later if needed.
        task = asyncio.create_task(self.start_charger(cp, queue))
        self._chargers[cp] = task

        return queue

    async def start_charger(self, charge_point, queue):
        """ Start listening for message of charger. """
        try:
            await charge_point.start()
        except Exception as error:
            logging.info(f"Charging station {charge_point.id} disconnected: {error}")
        finally:
            # Make sure to remove referenc to charger after it disconnected.
            del self._chargers[charge_point]

            # This will unblock the `on_connect()` handler and the connection
            # will be destroyed.
            await queue.put(True)

    async def view_chargers(self):
        chargers = []
        for charge_point, _ in self._chargers.items():
            chargers.append(charge_point.id)
        return chargers

    def get_charge_point(self, charge_point_id: str):
        for charge_point, task in self._chargers.items():
            if charge_point.id == charge_point_id:
                return charge_point, task
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Charging station {charge_point_id} not connected."
        )

    async def get_base_report(self, charge_point_id: str):
        charge_point, _ = self.get_charge_point(charge_point_id)
        return await charge_point.send_get_base_report()

    async def start_transaction(self, charge_point_id: str):
        charge_point, _ = self.get_charge_point(charge_point_id)
        return await charge_point.request_transaction_start()

    async def stop_transaction(self, charge_point_id: str):
        charge_point, _ = self.get_charge_point(charge_point_id)
        return await charge_point.request_transaction_stop()

    def disconnect_charger(self, charge_point_id: str):
        charge_point, task = self.get_charge_point(charge_point_id)
        task.cancel()


central_system = CentralSystem()

import asyncio
import logging
import uuid
from datetime import datetime

from ocpp.routing import on
from ocpp.v201 import call, call_result, ChargePoint
from ocpp.v201 import enums

logging.basicConfig(level=logging.INFO)


class ChargePointHandler(ChargePoint):
    @on(enums.Action.Authorize)
    async def on_authorize(self, **kwargs):
        logging.info("Authorization")
        return call_result.AuthorizePayload(
            id_token_info={
                "status": "Accepted"
            },
            certificate_status=None,
        )

    @on(enums.Action.GetBaseReport)
    async def on_get_base_report(self, **kwargs):
        logging.info("Base report")
        return call_result.GetBaseReportPayload(
            status="Accepted"
        )

    @on(enums.Action.GetReport)
    async def on_get_report(self, **kwargs):
        logging.info("Report")
        return call_result.GetReportPayload(
            status="Accepted"
        )

    @on(enums.Action.BootNotification)
    async def on_boot_notification(self, charging_station, reason, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status="Accepted"
        )

    @on(enums.Action.Heartbeat)
    async def on_heartbeat(self):
        logging.info("Got a heartbeat")
        return call_result.HeartbeatPayload(
            current_time=f"{datetime.utcnow():%Y-%m-%dT%H:%M:%S}Z"
        )

    @on(enums.Action.TransactionEvent)
    async def on_transaction_event(self, **kwargs):
        logging.info("Transaction event")
        return call_result.TransactionEventPayload(
            charging_priority=0
        )

    @on(enums.Action.RequestStartTransaction)
    async def on_request_start_transaction(self, **kwargs):
        logging.info("Transaction Start Requested")
        return call_result.RequestStartTransactionPayload(
            status=enums.RequestStartStopStatusType.accepted
        )

    @on(enums.Action.RequestStopTransaction)
    async def on_request_stop_transaction(self, **kwargs):
        logging.info("Transaction Stop Requested")
        return call_result.RequestStopTransactionPayload(
            status=enums.RequestStartStopStatusType.accepted
        )

    async def send_authorization(self, **kwargs):
        request = call.AuthorizePayload(
            id_token={
                "idToken": str(uuid.uuid4()),
                "type": "Local"
            }
        )
        await self.call(request)

    async def send_get_base_report(self, **kwargs):
        request = call.GetBaseReportPayload(
            request_id=111,
            report_base="SummaryInventory"
        )
        return await self.call(request)

    async def send_report(self):
        request = call.GetReportPayload(
            request_id=0
        )
        await self.call(request)

    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charging_station={
                "model": "Wallbox XYZ",
                "vendor_name": "anewone"
            },
            reason="PowerUp"
        )

        response = await self.call(request)

        if response.status == "Accepted":
            logging.info("Connected to central system.")
            await self.send_heartbeat(response.interval)

    async def send_heartbeat(self, interval):
        request = call.HeartbeatPayload()
        while True:
            await self.call(request)
            await asyncio.sleep(interval)

    async def send_transaction_event(self):
        request = call.TransactionEventPayload(
            event_type="Started",
            timestamp=f"{datetime.utcnow():%Y-%m-%dT%H:%M:%S}Z",
            trigger_reason="Authorized",
            seq_no=1,
            transaction_info={
                "transactionId": str(uuid.uuid4())
            },
        )
        return await self.call(request)

    async def request_transaction_start(self):
        request = call.RequestStartTransactionPayload(
            id_token={
                "idToken": str(uuid.uuid4()),
                "type": enums.IdTokenType.central
            },
            remote_start_id=0
        )
        return await self.call(request)

    async def request_transaction_stop(self):
        request = call.RequestStopTransactionPayload(
            transaction_id=str(uuid.uuid4())
        )
        return await self.call(request)

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def configure_tracer(service_name: str, host: str, port: int) -> None:
    trace.set_tracer_provider(TracerProvider(resource=Resource(attributes={"service.name": service_name})))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=host,
                agent_port=port,
            ),
        ),
    )
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


async def get_tracer() -> trace.Tracer:
    return trace.get_tracer(__name__)

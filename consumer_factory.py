from kafka import KafkaConsumer

def create_consumer(offset='earliest', value_deserializer = None) -> KafkaConsumer:
    return KafkaConsumer(
        'movielog9',   # 2 partitions on this topic can create 2 consumers to run in parallel
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset=offset,
        group_id='2fast2',
        # Commit that an offset has been read
        enable_auto_commit=True,
        # How often to tell Kafka, an offset has been read
        auto_commit_interval_ms=1000,
        fetch_max_bytes=100,
        max_poll_records = 10000,
        value_deserializer = value_deserializer
    )

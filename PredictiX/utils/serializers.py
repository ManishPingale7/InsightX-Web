from django.db.models.query import QuerySet

def predictions_serializer(data):
    serialized_data=[]
    if isinstance(data,QuerySet):
        for obj in data:
            serialized_obj={
                "id":obj.id,
                "name":obj.name,
                "user":obj.user.username,
                "air_temp":obj.air_temp,
                "process_temp":obj.process_temp,
                "rotational_speed":obj.rotational_speed,
                "torque":obj.torque,
                "tool_wear":obj.tool_wear,
                "quality":obj.quality,
                "predictions":obj.predictions
            }
            serialized_data.append(serialized_obj)
        return serialized_data

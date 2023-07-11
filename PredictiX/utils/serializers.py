from django.db.models.query import QuerySet

def predictions_serializer(data):
    serialized_data=[]
    if isinstance(data,QuerySet):
        for obj in data:
            serialized_obj={
                "id":obj.id,
                "machine_name":obj.machine_name,
                "user":obj.user.username,
                "password":obj.user.password,
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
    serialized_obj={
                "id":data.id,
                "machine_name":data.machine_name,
                "user":data.user.username,
                "password":data.user.password,
                "air_temp":data.air_temp,
                "process_temp":data.process_temp,
                "rotational_speed":data.rotational_speed,
                "torque":data.torque,
                "tool_wear":data.tool_wear,
                "quality":data.quality,
                "predictions":data.predictions
            }
    serialized_data.append(serialized_obj)
    return serialized_data

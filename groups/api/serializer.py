'''
Serializer for Group and Group Member
'''
from rest_framework import serializers
from groups.models import (Group, Member, MemberContactNumber)

class GroupSerializer(serializers.ModelSerializer):
    '''
    Serialzer class for App user Group
    '''
    class Meta:
        model = Group
        fields = ('id', 'app_user', 'name', 'description', 'member')

class MemberContactNumberSerializer(serializers.ModelSerializer):
    '''
    Serializer class for Member's Contact number
    '''
    class Meta:
        model = MemberContactNumber
        fields = ('id', 'phone', 'deleted_at')

class MemberSerializer(serializers.ModelSerializer):
    '''
    Serializer class for Group member details
    ''' 
    contact = MemberContactNumberSerializer(many=True)
    class Meta:
        model = Member
        fields = ('id', 'name', 'email', 'address', 'dob', 'contact', 'deleted_at')

    def create(self, validated_data):
        '''
        Overriding create method for adding contact entry with member detail
        '''
        member = Member.objects.create(name=validated_data.get('name'), 
                                        email=validated_data.get('email'), 
                                        address=validated_data.get('address'),
                                        dob=validated_data.get('dob'))
       
        contact_numbers = validated_data.pop('contact')
        contact_number_objects = [MemberContactNumber(member=member,phone=phone_number) for phone_number in contact_numbers]
        MemberContactNumber.objects.bulk_create(contact_number_objects)
        member.save()
        return member

    def update(self, instance, validated_data):
        '''
        Overiding update method for updating member+contact detail
        '''
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.address = validated_data.get('address', instance.address)
        instance.dob = validated_data.get('name', instance.dob)

        contact_numbers = validated_data.pop('contact')
        stored_contact_id = MemberContactNumber.objects.all().values_list('id', flat=True)
        for phone_number in contact_numbers:
            if getattr(phone_number, 'id') or phone_number.get('id',None) is not None:
                contact_obj = MemberContactNumber.objects.get(id=phone_number.id)
                contact_obj.phone = phone_number.get('phone')
                stored_contact_id.pop(phone_number.get('id'))
                contact_obj.save()
            else:
                new_contact_obj = MemberContactNumber.objects.create(member=instance, phone=phone_number.get('phone')) 
                
        MemberContactNumber.objects.filter(id__in=stored_contact_id).delete()
        instance.save()
        return instance

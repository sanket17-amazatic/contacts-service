"""
Serializer for Group and Group Member
"""
from rest_framework import serializers
from accounts.models import AppUser
from groups.models import (Group, Member, MemberContactNumber)

class MemberContactNumberSerializer(serializers.ModelSerializer):
    """
    Serializer class for Member's Contact number
    """
    class Meta:
        model = MemberContactNumber
        fields = ('id', 'phone', 'deleted_at')
        extra_kwargs = {'id': {'read_only': False, 'required':False}}

class MemberCreationAndUpdationMixin():
    """
    Member creation and updation mixin
    """
    def create(self, validated_data):
        """
        Overriding default create methods 
        Creating member and contact number
        """
        member = Member.objects.create(name=validated_data.get('name'), 
                                        email=validated_data.get('email'), 
                                        address=validated_data.get('address'),
                                        dob=validated_data.get('dob'))
        member.save()
        contact_numbers = validated_data.pop('contact')
        contact_number_objects = [MemberContactNumber(member=member,phone=phone_number['phone']) for phone_number in contact_numbers]
        MemberContactNumber.objects.bulk_create(contact_number_objects)
        return member

    def update(self, instance, validated_data):
        """
        Overiding update method for updating member+contact detail
        """
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.address = validated_data.get('address', instance.address)
        instance.dob = validated_data.get('dob', instance.dob)
        
        contact_numbers = validated_data.pop('contact')
        stored_contact_id_list = list(MemberContactNumber.objects.filter(member = instance.id).values_list('id', flat=True))
        for phone_number in contact_numbers:
            if phone_number.get('id',None) is not None:
                contact_obj = MemberContactNumber.objects.get(id=phone_number.get('id'))
                if contact_obj.phone != phone_number.get('phone'):
                    contact_obj.phone = phone_number.get('phone')
                stored_contact_id_list.remove(phone_number.get('id'))
                contact_obj.save()
            else:
                new_contact_obj = MemberContactNumber.objects.create(member=instance, phone=phone_number.get('phone')) 
                
        MemberContactNumber.objects.filter(id__in=stored_contact_id_list).delete()
        instance.save()
        return instance

class MemberSerializer(MemberCreationAndUpdationMixin, serializers.ModelSerializer):
    """
    Serializer class for Group member details
    """ 
    contact = MemberContactNumberSerializer(many=True,read_only=False)
    class Meta:
        model = Member
        fields = ('id', 'name', 'email', 'address', 'dob', 'contact', 'deleted_at')

class GroupSerializer(MemberCreationAndUpdationMixin, serializers.ModelSerializer):
    """
    Serialzer class for App user Group
    """
    member = MemberSerializer(many=True)
    class Meta:
        model = Group
        fields = ('id', 'app_user', 'name', 'description', 'member')

    def create(self, validated_data):
        """
        Overriding default create method to create groups
        """
        group = Group.objects.create(app_user=validated_data.get('app_user'),
                                    name=validated_data.get('name'),
                                    description=validated_data.get('description'))
        group.save()
        if validated_data.get('member') is not None:
            req_member_data = validated_data.pop('member')
            for member_data in req_member_data:
                group_member = super().create(dict(member_data))
                group.member.add(group_member)
        return group

    def update(self, instance, validated_data):
        """
        Overiding update method for updating groups
        """
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('email', instance.description)
        instance.app_user = validated_data.get('app_user', instance.app_user)
        print(validated_data.get('member'))
        if validated_data.get('member'):        
            req_group_member = validated_data.pop('member')
            stored_member_id_list = list(Member.objects.filter(group_members__id = instance.id).values_list('id', flat=True))

            for group_member in req_group_member:
                if group_member.get('id',None) is not None:
                    contact_obj = super().update(group_member)
                    stored_member_id_list.remove(group_member.get('id'))
                else:
                    new_group_member_obj = super().create(dict(group_member))
                    instance.member.add(new_group_member_obj) 
            for member_id in stored_member_id_list:
                member_object = Member.objects.get(id=member_id)       
                instance.member.remove(member_object)
        instance.save() 
        return instance

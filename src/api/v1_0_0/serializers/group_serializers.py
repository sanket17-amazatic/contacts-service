"""
Serializer for Group and Group Member
"""
from rest_framework import serializers
from account.models import AppUser
from group.models import (Group, Contact, ContactNumber)

class ContactNumberSerializer(serializers.ModelSerializer):
    """
    Serializer class for Member's Contact number
    """
    class Meta:
        model = ContactNumber
        fields = ('id', 'phone', 'deleted_at')
        extra_kwargs = {'id': {'read_only': False, 'required':False}}

class ContactCreationAndUpdationMixin():
    """
    Contact creation and updation mixin
    """
    def create(self, validated_data):
        """
        Overriding default create methods 
        Creating contact and contact number
        """
        member = Contact.objects.create(name=validated_data.get('name'), 
                                        email=validated_data.get('email'), 
                                        address=validated_data.get('address'),
                                        dob=validated_data.get('dob'))
        member.save()
        contact_numbers = validated_data.pop('contact')
        contact_number_objects = [ContactNumber(member=member,phone=phone_number['phone']) for phone_number in contact_numbers]
        ContactNumber.objects.bulk_create(contact_number_objects)
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
        stored_contact_id_list = list(ContactNumber.objects.filter(member = instance.id).values_list('id', flat=True))
        for phone_number in contact_numbers:
            if phone_number.get('id',None) is not None:
                contact_obj = ContactNumber.objects.get(id=phone_number.get('id'))
                if contact_obj.phone != phone_number.get('phone'):
                    contact_obj.phone = phone_number.get('phone')
                stored_contact_id_list.remove(phone_number.get('id'))
                contact_obj.save()
            else:
                new_contact_obj = ContactNumber.objects.create(member=instance, phone=phone_number.get('phone')) 
                
        ContactNumber.objects.filter(id__in=stored_contact_id_list).delete()
        instance.save()
        return instance

class ContactSerializer(ContactCreationAndUpdationMixin, serializers.ModelSerializer):
    """
    Serializer class for Group contact details
    """ 
    contact = ContactNumberSerializer(many=True,read_only=False)
    class Meta:
        model = Contact
        fields = ('id', 'name', 'email', 'address', 'dob', 'contact', 'deleted_at')

class GroupSerializer(ContactCreationAndUpdationMixin, serializers.ModelSerializer):
    """
    Serialzer class for App user Group
    """
    contacts = ContactSerializer(many=True)
    class Meta:
        model = Group
        fields = ('id', 'app_user', 'name', 'description', 'contacts')

    def create(self, validated_data):
        """
        Overriding default create method to create groups
        """
        group = Group.objects.create(app_user=validated_data.get('app_user'),
                                    name=validated_data.get('name'),
                                    description=validated_data.get('description'))
        group.save()
        if validated_data.get('contacts') is not None:
            req_member_data = validated_data.pop('contacts')
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
        if validated_data.get('contacts'):        
            req_group_contact = validated_data.pop('contacts')
            stored_contact_id_list = list(Contact.objects.filter(group_contacts__id = instance.id).values_list('id', flat=True))

            for group_contact in req_group_contact:
                if group_contact.get('id',None) is not None:
                    contact_obj = super().update(group_contact)
                    stored_contact_id_list.remove(group_contact.get('id'))
                else:
                    new_group_contact_obj = super().create(dict(group_contact))
                    instance.contacts.add(new_group_contact_obj) 
            for contact_id in stored_contact_id_list:
                contact_object = Contact.objects.get(id=contact_id)       
                instance.contacts.remove(contact_object)
        instance.save() 
        return instance

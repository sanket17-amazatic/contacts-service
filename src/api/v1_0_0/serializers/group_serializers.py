"""
Serializer for Group and Group Member
"""
from django.db import transaction
from django.db.models import (Q,)
from rest_framework import serializers
from user.models import User
from group.models import (Group, Contact, ContactNumber, ContactEmail, Member)
from .user_serializers import UserSerializer

class ContactNumberSerializer(serializers.ModelSerializer):
    """
    Serializer class for Member's Contact number
    """
    class Meta:
        model = ContactNumber
        fields = ('id', 'phone', 'deleted_at')
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

class ContactEmailSerializer(serializers.ModelSerializer):
    """
    Serializer class for Contact Member's email
    """
    class Meta:
        model = ContactEmail
        fields = ('id', 'email', 'deleted_at')
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

class ContactCreationAndUpdationMixin():
    """
    Contact creation and updation mixin
    """
    @transaction.atomic
    def create(self, validated_data):
        """
        Overriding default create methods 
        Creating contact and contact number
        """
        member = Contact.objects.create(first_name=validated_data.get('first_name'),
                                        last_name=validated_data.get('last_name'),
                                        company=validated_data.get('company'),
                                        address=validated_data.get('address'),
                                        dob=validated_data.get('dob'))
        member.save()
        contact_numbers = validated_data.pop('contact')
        if not contact_numbers:
                raise serializers.ValidationError('Contact Number is required')
        contact_number_objects = [ContactNumber(contact=member, phone=phone_number['phone']) for phone_number in contact_numbers]
        ContactNumber.objects.bulk_create(contact_number_objects)

        contact_emails = validated_data.pop('email')
        contact_email_objects = [ContactEmail(contact=member, email=email['email']) for email in contact_emails]
        ContactEmail.objects.bulk_create(contact_email_objects)
        return member

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Overiding update method for updating member+contact detail
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.company = validated_data.get('company', instance.company)
        instance.address = validated_data.get('address', instance.address)
        instance.dob = validated_data.get('dob', instance.dob)

        contact_numbers = validated_data.pop('contact')
        stored_contact_id_list = list(ContactNumber.objects.filter(contact=instance.id).values_list('id', flat=True))
        for phone_number in contact_numbers:
            if phone_number.get('id', None) is not None:
                contact_obj = ContactNumber.objects.get(id=phone_number.get('id'))
                if contact_obj.phone != phone_number.get('phone'):
                    contact_obj.phone = phone_number.get('phone')
                stored_contact_id_list.remove(phone_number.get('id'))
                contact_obj.save()
            else:
                new_contact_obj = ContactNumber.objects.create(contact=instance, phone=phone_number.get('phone'))

        ContactNumber.objects.filter(id__in=stored_contact_id_list).delete()

        contact_emails = validated_data.pop('email')
        stored_contact_id_list_for_email = list(ContactEmail.objects.filter(contact=instance.id).values_list('id', flat=True))
        for email_rec in contact_emails:
            if email_rec.get('id', None) is not None:
                contact_email_obj = ContactEmail.objects.get(id=email_rec.get('id'))
                if contact_email_obj.email != email_rec.get('email'):
                    contact_email_obj.email = email_rec.get('email')
                stored_contact_id_list_for_email.remove(email_rec.get('id'))
                contact_email_obj.save()
            else:
                new_contact_email_obj = ContactEmail.objects.create(
                    contact=instance, email=email_rec.get('email'))

        ContactEmail.objects.filter(id__in=stored_contact_id_list_for_email).delete()

        instance.save()
        return instance

class ContactSerializer(ContactCreationAndUpdationMixin, serializers.ModelSerializer):
    """
    Serializer class for Group contact details
    """
    contact = ContactNumberSerializer(many=True, read_only=False)
    email = ContactEmailSerializer(many=True, read_only=False)

    class Meta:
        model = Contact
        fields = ('id', 'first_name', 'last_name', 'company',
                  'address', 'dob', 'email', 'contact', 'deleted_at')

class MemberSerializer(serializers.ModelSerializer):
    """
    Serializer class for group members
    """
    user = UserSerializer(read_only=True)
    class Meta:
        model = Member
        fields = ('id', 'group', 'user', 'role_type', 'display_name')
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def valdiate(self, data):
        """
        Validating method to check for requested user valid role
        """
        group = data.get('group')
        user = data.get('user')

        group = Group.object.filter(id=group)
        if group is None:
            raise serializers.ValidationError('No such group present')

        user = User.objects.filter(id=user)
        if user is None:
            raise serializers.ValidationError('No such user present')

        return data

    def create(self, validated_data):
        """
        Overriding default create
        Creating reln between group and member
        """
        
        new_member = Member.object.create(
            group=validated_data.get('group'), user=validated_data.get('user'), role_type=validated_data.get('role_type'), display_name=validated_data.get('display_name'))
        new_member.save()
        return new_member

    def update(self, instance, validated_data):
        """
        Overriding default update
        Check for requested user is admin or owner
        """
        instance.group = validated_data.get('group', instance.group)
        instance.user = validated_data.get('user', instance.user)
        instance.role_type = validated_data.get('role_type', instance.role_type)
        instance.display_name = validated_data.get('display_name', instance.display_name)
        instance.save()
        return instance

class GroupSerializer(ContactCreationAndUpdationMixin, serializers.ModelSerializer):
    """
    Serialzer class for App user Group
    """
    contacts = ContactSerializer(many=True)
    members = MemberSerializer(many=True, read_only=True)
    owner = serializers.CharField(max_length=15, read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'description', 'contacts', 'members', 'owner')

    @transaction.atomic
    def create(self, validated_data):
        """
        Overriding default create method to create groups
        """
        req_user = self.context['request'].user
        group = Group.objects.create(name=validated_data.get('name'),
                                     description=validated_data.get('description'))
        group.save()
        if validated_data.get('contacts') is not None:
            req_contact_data = validated_data.pop('contacts')
            for contact_data in req_contact_data:
                group_contact = super().create(dict(contact_data))
                group.contacts.add(group_contact)
        print('****', req_user.phone)
        owner = User.objects.filter(phone=req_user.phone).first()
        print(owner)
        owner_member = Member.objects.create(
            group=group, user=req_user, role_type='owner', display_name=owner.name)
        owner_member.save()

        if validated_data.get('members') is not None:
            req_member_data = validated_data.pop('members')
            for member_data in req_member_data:
                if member_data.get('phone') == req_user.phone:
                    continue
                else:
                    user = User.objects.filter(phone=req_member_data.get('phone'))
                    new_member = Member.objects.create(
                        group=group, user=user, role_type=member_data.get('role_type'), display_name=member_data.get('display_name'))
                    new_member.save()
        
        return group

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Overiding update method for updating groups
        """
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)

        if validated_data.get('contacts'):
            req_group_contact = validated_data.pop('contacts')
            stored_contact_id_list = list(Contact.objects.filter(
                contact_groups__id=instance.id).values_list('id', flat=True))

            for group_contact in req_group_contact:
                if group_contact.get('id', None) is not None:
                    contact_obj = super().update(group_contact)
                    stored_contact_id_list.remove(group_contact.get('id'))
                else:
                    new_group_contact_obj = super().create(dict(group_contact))
                    instance.contacts.add(new_group_contact_obj)
            for contact_id in stored_contact_id_list:
                contact_object = Contact.objects.get(id=contact_id)
                instance.contacts.remove(contact_object)

        if validated_data.get('members'):
            req_group_member = validated_data.pop('members')
            stored_member = list(Member.objects.filter(group=instance.id).values_list('user', flat=True))
            for group_member in req_group_member:
                if group_member.get('id',None) is not None:
                    user_id = Member.objects.filter(id=group_member.get('id')).values('user')
                    stored_member.remove(user_id[0]['user'])
                else:
                    user = User.objects.filter(phone=group_member.get('phone'))
                    if user is not None:
                        new_member = Member.objects.create(
                            group=instance.id, user=user, role_type=group_member.get('role_type'), display_name=group_member.get('display_name'))
                        new_member.save()
           
            Member.objects.filter(user__in=stored_member).delete()

        instance.save()
        return instance

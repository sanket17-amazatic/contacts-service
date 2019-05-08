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
                                        last_name=validated_data.get(
                                            'last_name'),
                                        company=validated_data.get('company'),
                                        address=validated_data.get('address'),
                                        dob=validated_data.get('dob'))
        member.save()
        contact_numbers = validated_data.pop('contact')
        contact_number_objects = [ContactNumber(
            contact=member, phone=phone_number['phone']) for phone_number in contact_numbers]
        ContactNumber.objects.bulk_create(contact_number_objects)

        contact_emails = validated_data.pop('email')
        contact_email_objects = [ContactEmail(
            contact=member, email=email['email']) for email in contact_emails]
        ContactEmail.objects.bulk_create(contact_email_objects)
        return member

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Overiding update method for updating member+contact detail
        """
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.address = validated_data.get('address', instance.address)
        instance.dob = validated_data.get('dob', instance.dob)

        contact_numbers = validated_data.pop('contact')
        stored_contact_id_list = list(ContactNumber.objects.filter(
            contact=instance.id).values_list('id', flat=True))
        for phone_number in contact_numbers:
            if phone_number.get('id', None) is not None:
                contact_obj = ContactNumber.objects.get(
                    id=phone_number.get('id'))
                if contact_obj.phone != phone_number.get('phone'):
                    contact_obj.phone = phone_number.get('phone')
                stored_contact_id_list.remove(phone_number.get('id'))
                contact_obj.save()
            else:
                new_contact_obj = ContactNumber.objects.create(
                    contact=instance, phone=phone_number.get('phone'))

        ContactNumber.objects.filter(id__in=stored_contact_id_list).delete()

        contact_emails = validated_data.pop('email')
        stored_contact_id_list_for_email = list(ContactEmail.objects.filter(
            contact=instance.id).values_list('id', flat=True))
        for email_rec in contact_emails:
            if email_rec.get('id', None) is not None:
                contact_email_obj = ContactEmail.objects.get(
                    id=email_rec.get('id'))
                if contact_email_obj.email != email_rec.get('email'):
                    contact_email_obj.email = email_rec.get('email')
                stored_contact_id_list_for_email.remove(email_rec.get('id'))
                contact_email_obj.save()
            else:
                new_contact_email_obj = ContactEmail.objects.create(
                    contact=instance, email=email_rec.get('email'))

        ContactEmail.objects.filter(
            id__in=stored_contact_id_list_for_email).delete()

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


def check_user_validity(user):
    """
    Checks the request user is admin or owner of group
    """
    if user in None:
        raise serializers.ValidationError(
            'Requested user is not a member of this group')
    if user.role != 'ADMIN' or user.role != 'OWNER':
        raise serializers.ValidationError(
            'Requested user has no permission for this operation')
    else:
        return True


class MemberSerializer(serializers.ModelSerializer):
    """
    Serializer class for group members
    """
    class Meta:
        model = Member
        fields = ('id', 'group', 'user', 'roles')
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def valdiate(self, data):
        """
        """
        group_id = data.get('group')
        user_id = data.get('user')

        group = Group.object.filter(id=group_id)
        if group is None:
            raise serializers.ValidationError('No such group present')

        user = User.objects.filter(id=user_id)
        if user is None:
            raise serializers.ValidationError('No such user present')

        req_user = self.context['request'].user
        valid_user = Member.object.filter(user=req_user, group=group)
        if check_user_validity(valid_user):
            return data

    def create(self, validated_data):
        """
        Overriding default create
        Creating reln between group and member
        """
        new_member = Member.object.create(
            group=validated_data.get('group'), user=validated_data.get('user'), role=validated_data.get('role'))
        new_member.save()
        return new_member

    def update(self, instance, validated_data):
        """
        Overriding default update
        Check for requested user is admin or owner
        """
        instance.group = validated_data.get('group', instance.group)
        instance.user = validated_data.get('user', instance.user)
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance


class GroupSerializer(ContactCreationAndUpdationMixin, serializers.ModelSerializer):
    """
    Serialzer class for App user Group
    """
    contacts = ContactSerializer(many=True)
    members = MemberSerializer(many=True)

    class Meta:
        model = Group
        fields = ('id', 'owner', 'name', 'description', 'contacts', 'members')

    @transaction.atomic
    def create(self, validated_data):
        """
        Overriding default create method to create groups
        """
        group = Group.objects.create(owner=validated_data.get('owner'),
                                     name=validated_data.get('name'),
                                     description=validated_data.get('description'))
        group.save()
        if validated_data.get('contacts') is not None:
            req_contact_data = validated_data.pop('contacts')
            for contact_data in req_contact_data:
                group_contact = super().create(dict(contact_data))
                group.contacts.add(group_contact)

        if validated_data.get('members') is not None:
            req_member_data = validated_data.pop('members')
            for member_data in req_member_data:
                if member_data.user == group.owner:
                    continue
                else:
                    owner_member = Member.objects.create(
                        group=group, user=member_data.user, role=member_data.role)
                    owner_member.save()
        else:
            owner_member = Member.objects.create(
                group=group.id, user=group.owner.id, role='OWN')
            owner_member.save()
        return group

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Overiding update method for updating groups
        """
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'email', instance.description)
        instance.app_user = validated_data.get('app_user', instance.app_user)

        if validated_data.get('contacts'):
            req_group_contact = validated_data.pop('contacts')
            stored_contact_id_list = list(Contact.objects.filter(
                group_contacts__id=instance.id).values_list('id', flat=True))

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
            stored_member = Member.objects.filter(group=instance.id)

            for group_member in req_group_member:
                if group_member in stored_member:
                    stored_member.remove(group_member)
                else:
                    new_member = Member.objects.create(
                        group=instance.id, user=group_member.user, role=group_member.role)
                    new_member.save()
            for member in stored_member:
              member.delete()

        instance.save()
        return instance

    def delete(self, instance):
        """
        Overrding default delete
        """
        req_user = self.context['request'].user
        valid_user = Member.object.filter(
            user=req_user).filter(group=instance)
        if check_user_validity(valid_user):
            return instance.delete()

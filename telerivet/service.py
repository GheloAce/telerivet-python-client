
from .entity import Entity
        
class Service(Entity):
    """
    Represents an automated service on Telerivet, for example a poll, auto-reply, webhook service,
    etc.
    
    A service, generally, defines some automated behavior that can be
    invoked/triggered in a particular context, and may be invoked either manually or when a
    particular event occurs.
    
    Most commonly, services work in the context of a particular message, when the
    message is originally received by Telerivet.
    
    Fields:
    
      - id (string, max 34 characters)
          * ID of the service
          * Read-only
      
      - name
          * Name of the service
          * Updatable via API
      
      - active (bool)
          * Whether the service is active or inactive. Inactive services are not automatically
              triggered and cannot be invoked via the API.
          * Updatable via API
      
      - priority (int)
          * A number that determines the order that services are triggered when a particular event
              occurs (smaller numbers are triggered first). Any service can determine whether or not
              execution "falls-through" to subsequent services (with larger priority values) by setting
              the return_value variable within Telerivet's Rules Engine.
          * Updatable via API
      
      - contexts (dict)
          * A key/value map where the keys are the names of contexts supported by this service (e.g.
              message, contact), and the values are themselves key/value maps where the keys are event
              names and the values are all true. (This structure makes it easy to test whether a service
              can be invoked for a particular context and event.)
          * Read-only
      
      - vars (dict)
          * Custom variables stored for this service
          * Updatable via API
      
      - project_id
          * ID of the project this service belongs to
          * Read-only
      
    """

    def invoke(self, **options):
        """
        Manually invoke this service in a particular context.
        
        For example, to send a poll to a particular contact (or resend the
        current question), you can invoke the poll service with context=contact, and contact_id as
        the ID of the contact to send the poll to.
        
        Or, to manually apply a service for an incoming message, you can
        invoke the service with context=message, event=incoming_message, and message_id as the ID of
        the incoming message. (This is normally not necessary, but could be used if you want to
        override Telerivet's standard priority-ordering of services.)
        
        Arguments:
              * Required
            
            - context
                * The name of the context in which this service is invoked
                * Allowed values: message, contact, project, receipt
                * Required
            
            - event
                * The name of the event that is triggered (must be supported by this service)
                * Default: default
            
            - message_id
                * The ID of the message this service is triggered for
                * Required if context is 'message'
            
            - contact_id
                * The ID of the contact this service is triggered for
                * Required if context is 'contact'
          
        """
        
        invoke_result = self._api.doRequest('POST', self.getBaseApiPath() + '/invoke', options)
        
        if 'sent_messages' in invoke_result:
            from .message import Message
        
            sent_messages = []
            for sent_message_data in invoke_result['sent_messages']:
                sent_messages.append(Message(self._api, sent_message_data))
            
            invoke_result['sent_messages'] = sent_messages
            
        return invoke_result

    def getContactState(self, contact):
        """
        Gets the current state for a particular contact for this service.
        
        If the contact doesn't already have a state, this method will return
        a valid state object with id=null. However this object would not be returned by
        queryContactStates() unless it is saved with a non-null state id.
        
        Arguments:
          - contact (Contact)
              * The contact whose state you want to retrieve.
              * Required
          
        Returns:
            ContactServiceState
        """    
        from .contactservicestate import ContactServiceState
        return ContactServiceState(self._api, self._api.doRequest('GET', self.getBaseApiPath() + '/states/' + contact.id))
        
    def setContactState(self, contact, **options):
        """
        Initializes or updates the current state for a particular contact for the given service. If
        the state id is null, the contact's state will be reset.
        
        Arguments:
          - contact (Contact)
              * The contact whose state you want to update.
              * Required
          
              * Required
            
            - id (string, max 63 characters)
                * Arbitrary string representing the contact's current state for this service, e.g.
                    'q1', 'q2', etc.
                * Required
            
            - vars (dict)
                * Custom variables stored for this contact's state
          
        Returns:
            ContactServiceState
        """
        from .contactservicestate import ContactServiceState
        return ContactServiceState(self._api, self._api.doRequest('POST', self.getBaseApiPath() + '/states/' + contact.id, options))        
    
    def resetContactState(self, contact):
        """
        Resets the current state for a particular contact for the given service.
        
        Arguments:
          - contact (Contact)
              * The contact whose state you want to reset.
              * Required
          
        Returns:
            ContactServiceState
        """
        from .contactservicestate import ContactServiceState
        return ContactServiceState(self._api, self._api.doRequest('DELETE', self.getBaseApiPath() + '/states/' + contact.id))

    def queryContactStates(self, **options):
        """
        Query the current states of contacts for this service.
        
        Arguments:
            
            - id
                * Filter states by id
                * Allowed modifiers: id[ne], id[prefix], id[not_prefix], id[gte], id[gt], id[lt],
                    id[lte]
            
            - vars (dict)
                * Filter states by value of a custom variable (e.g. vars[email], vars[foo], etc.)
                * Allowed modifiers: vars[foo][exists], vars[foo][ne], vars[foo][prefix],
                    vars[foo][not_prefix], vars[foo][gte], vars[foo][gt], vars[foo][lt], vars[foo][lte],
                    vars[foo][min], vars[foo][max]
            
            - sort
                * Sort the results based on a field
                * Allowed values: default
                * Default: default
            
            - sort_dir
                * Sort the results in ascending or descending order
                * Allowed values: asc, desc
                * Default: asc
            
            - page_size (int)
                * Number of results returned per page (max 200)
                * Default: 50
            
            - offset (int)
                * Number of items to skip from beginning of result set
                * Default: 0
          
        Returns:
            APICursor (of ContactServiceState)
        """
        from .contactservicestate import ContactServiceState
        return self._api.newApiCursor(ContactServiceState, self.getBaseApiPath() + "/states", options)

    def save(self):
        """
        Saves any fields or custom variables that have changed for this service.
        
        """
        super(Service, self).save()

    def getBaseApiPath(self):
        return "/projects/%(project_id)s/services/%(id)s" % {'project_id': self.project_id, 'id': self.id} 
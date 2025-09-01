# SharePoint Document Manager with User Authentication

This application now supports **user-based authentication** with SharePoint instead of app-only authentication. Users can log in with their Microsoft 365 credentials to access and manage documents.

## 🔐 **Authentication Methods**

### 1. **Interactive User Login** (Primary Method)
- Users enter their Microsoft 365 username and password
- Credentials are used directly for SharePoint authentication
- No need for app registration or client secrets
- More secure and user-friendly

### 2. **Access Token Authentication** (Alternative)
- For web applications that already have user tokens
- Supports OAuth 2.0 flow integration
- Useful for enterprise SSO scenarios

## 🚀 **Key Benefits of User Authentication**

✅ **Enhanced Security**: Users authenticate with their own credentials  
✅ **No App Registration**: Eliminates the need for Azure AD app setup  
✅ **User Permissions**: Respects individual SharePoint access rights  
✅ **Audit Trail**: All actions are logged with user identity  
✅ **Simplified Setup**: No complex configuration required  

## 📋 **Prerequisites**

### **User Requirements**
- Microsoft 365 account with access to `https://cpncorp.sharepoint.com/sites/askcal`
- Valid network credentials (username/password)
- Access to the specified SharePoint folders

### **System Requirements**
- Python 3.8+
- Office365-REST-Python-Client library
- Network access to SharePoint Online

## 🛠️ **Installation & Setup**

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Start the Application**
```bash
# For Azure Functions
func start

# For local development
python server/start_python_server.py
```

### 3. **Access the Application**
- Open your browser to the application URL
- You'll see a login screen
- Enter your Microsoft 365 credentials
- Start managing SharePoint documents!

## 🔑 **How Authentication Works**

### **Login Process**
1. User enters username and password
2. Application creates SharePoint context with user credentials
3. SharePoint validates the credentials
4. If successful, user gains access to their authorized folders
5. All subsequent operations use the authenticated user context

### **Security Features**
- **No Credential Storage**: Passwords are never stored or logged
- **Session Management**: Authentication persists during the session
- **Automatic Logout**: Session ends when user logs out or closes browser
- **Permission Respect**: Users can only access folders they have permission for

## 📁 **SharePoint Folder Access**

The application works with these configured folders:
- **Boarddeck** - Board meeting materials
- **TRC** - Technical Review Committee  
- **Human Resources** - HR documents
- **Etaf Contracts** - Contract documentation
- **PJM** - PJM-related documents
- **Trading Compliance** - Compliance policies

**Note**: Users can only access folders they have permission to view/edit in SharePoint.

## 🎯 **API Endpoints**

### **Authentication**
```
POST /api/sharepoint-auth
{
  "action": "login",
  "username": "user@cpncorp.com",
  "password": "userpassword"
}
```

### **Get User Info**
```
GET /api/sharepoint-auth
```

### **Logout**
```
POST /api/sharepoint-auth
{
  "action": "logout"
}
```

### **Document Operations** (Requires Authentication)
- `GET /api/files` - List documents
- `POST /api/upload` - Upload files
- `POST /api/extract-text/{file_url}` - Extract text
- `DELETE /api/files/{filename}` - Delete files
- `GET /api/files/{file_url}/download` - Get download URL

## 🔒 **Security Considerations**

### **Credential Handling**
- Passwords are transmitted securely over HTTPS
- No credential caching or storage
- Each operation reuses the authenticated session
- Automatic session timeout

### **Access Control**
- Users can only access folders they have permission for
- File operations respect SharePoint permissions
- No elevation of privileges
- Audit logging of all actions

### **Network Security**
- All communication uses HTTPS
- SharePoint API calls are authenticated
- No sensitive data in logs
- Secure session management

## 🚨 **Troubleshooting**

### **Common Login Issues**

1. **Invalid Credentials**
   - Verify username format (e.g., `username@cpncorp.com`)
   - Check password is correct
   - Ensure account is not locked

2. **Access Denied**
   - Verify user has access to SharePoint site
   - Check folder permissions
   - Contact SharePoint administrator

3. **Network Issues**
   - Check internet connectivity
   - Verify firewall settings
   - Ensure SharePoint Online is accessible

### **Authentication Errors**

```bash
# Check Azure Functions logs
func logs

# Common error messages:
# - "User not authenticated" - Need to log in first
# - "Invalid username or password" - Check credentials
# - "Access denied" - Permission issue
```

## 🔄 **Migration from App-Only Auth**

If you were using the previous app-only authentication:

1. **Remove Environment Variables**:
   - `SHAREPOINT_CLIENT_ID`
   - `SHAREPOINT_CLIENT_SECRET` 
   - `SHAREPOINT_TENANT_ID`

2. **Update Azure Functions**:
   - Replace `shared/sharepoint_storage.py` with `shared/sharepoint_user_auth.py`
   - Update function imports

3. **Test User Login**:
   - Verify users can authenticate
   - Check folder access permissions
   - Test document operations

## 📱 **User Experience**

### **Login Screen**
- Clean, professional interface
- Clear instructions for credentials
- Helpful error messages
- Responsive design

### **Main Application**
- Welcome message with user name
- Current user display
- Easy logout option
- Folder-based document management

### **Security Indicators**
- Authentication status display
- User identity confirmation
- Secure session indicators
- Clear logout confirmation

## 🚀 **Future Enhancements**

### **Planned Features**
- **Multi-Factor Authentication** (MFA) support
- **Single Sign-On** (SSO) integration
- **Role-Based Access Control** (RBAC)
- **Advanced Audit Logging**
- **Session Timeout Configuration**

### **Enterprise Features**
- **Active Directory** integration
- **Group Policy** support
- **Conditional Access** policies
- **Compliance Reporting**

## 📞 **Support & Contact**

### **Technical Support**
- Check application logs for errors
- Verify SharePoint permissions
- Test with different user accounts
- Review network connectivity

### **SharePoint Administration**
- Contact your SharePoint admin for folder permissions
- Verify site access rights
- Check user account status
- Review security policies

## 📄 **License & Compliance**

This application is designed to work with Microsoft 365 and SharePoint Online. Users must comply with their organization's security policies and data handling requirements.

---

**Note**: This user authentication approach provides a more secure and user-friendly experience compared to app-only authentication, while maintaining all the document management functionality.

# 🔧 Guide de dépannage Email

## ❌ Problèmes courants et solutions

### **1. Erreur "Authentication failed"**
**Cause** : Mauvais mot de passe d'application
**Solution** :
- Régénérer un nouveau mot de passe d'application
- Vérifier que l'authentification à 2 facteurs est activée
- Utiliser le mot de passe de 16 caractères, pas votre mot de passe Gmail

### **2. Erreur "SMTP server connection failed"**
**Cause** : Problème de réseau ou de configuration
**Solution** :
- Vérifier que `smtp.gmail.com` et port `587` sont corrects
- Vérifier votre connexion internet
- Essayer avec un autre réseau si possible

### **3. Erreur "Username and Password not accepted"**
**Cause** : Compte Gmail non configuré pour les applications
**Solution** :
- Aller dans [myaccount.google.com/lesssecureapps](https://myaccount.google.com/lesssecureapps)
- Activer "Autoriser les applications moins sécurisées" (si disponible)
- Sinon, utiliser un mot de passe d'application

### **4. Erreur "Quota exceeded"**
**Cause** : Limite d'envoi Gmail atteinte
**Solution** :
- Gmail : 500 emails/jour pour les comptes gratuits
- Attendre 24h ou utiliser un autre compte

### **5. Email reçu dans les spams**
**Cause** : Filtres anti-spam
**Solution** :
- Marquer l'expéditeur comme "non spam"
- Ajouter l'adresse dans vos contacts
- Vérifier les paramètres de votre boîte mail

## 🔍 Vérifications à faire

### **Configuration Gmail**
- [ ] Authentification à 2 facteurs activée
- [ ] Mot de passe d'application généré
- [ ] Mot de passe copié correctement (16 caractères)

### **Configuration application**
- [ ] Adresse email correcte
- [ ] Serveur SMTP : `smtp.gmail.com`
- [ ] Port : `587`
- [ ] Nom d'utilisateur : votre email Gmail complet
- [ ] Mot de passe : mot de passe d'application (pas votre mot de passe Gmail)

### **Test de connexion**
- [ ] Bouton "Test" fonctionne
- [ ] Email de test reçu
- [ ] Pas d'erreur dans les logs

## 📞 Support

Si les problèmes persistent :
1. Vérifiez les logs de l'application
2. Testez avec un autre compte Gmail
3. Contactez le support technique

## 🔐 Sécurité

- **Ne partagez jamais** votre mot de passe d'application
- **Utilisez un compte dédié** pour l'application si possible
- **Surveillez** les connexions dans votre compte Google
- **Régénérez** le mot de passe d'application si compromis 
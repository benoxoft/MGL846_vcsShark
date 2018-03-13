use testRun
db.dropUser("root")
db.createUser( { user: "root",
                 pwd: "balla1234$",
                 roles: [ { role: "clusterAdmin", db: "admin" },
                          { role: "readAnyDatabase", db: "admin" },
                          "readWrite"] },
               { w: "majority" , wtimeout: 5000 } )

use admin
db.dropUser("root")
db.createUser(
   {
     user: "root",
     pwd: "balla1234$",
     roles:
       [
         { role: "readWrite", db: "config" },
         "clusterAdmin"
       ]
   }
)
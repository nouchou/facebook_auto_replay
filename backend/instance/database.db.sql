BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "auto_response" (
	"id"	INTEGER NOT NULL,
	"trigger_keyword"	VARCHAR(200) NOT NULL,
	"response_text"	TEXT NOT NULL,
	"response_type"	VARCHAR(50),
	"is_active"	BOOLEAN,
	"priority"	INTEGER,
	"created_at"	DATETIME,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "comment" (
	"id"	INTEGER NOT NULL,
	"comment_id"	VARCHAR(100),
	"post_id"	VARCHAR(100),
	"user_id"	VARCHAR(100),
	"user_name"	VARCHAR(200),
	"comment_text"	TEXT,
	"response_sent"	TEXT,
	"is_automated"	BOOLEAN,
	"timestamp"	DATETIME,
	"page_id"	INTEGER,
	UNIQUE("comment_id"),
	PRIMARY KEY("id"),
	FOREIGN KEY("page_id") REFERENCES "facebook_page"("id")
);
CREATE TABLE IF NOT EXISTS "facebook_page" (
	"id"	INTEGER NOT NULL,
	"page_id"	VARCHAR(100) NOT NULL,
	"page_name"	VARCHAR(200),
	"access_token"	TEXT NOT NULL,
	"is_active"	BOOLEAN,
	"created_at"	DATETIME,
	PRIMARY KEY("id"),
	UNIQUE("page_id")
);
CREATE TABLE IF NOT EXISTS "message" (
	"id"	INTEGER NOT NULL,
	"message_id"	VARCHAR(100),
	"sender_id"	VARCHAR(100),
	"sender_name"	VARCHAR(200),
	"message_text"	TEXT,
	"response_sent"	TEXT,
	"is_automated"	BOOLEAN,
	"timestamp"	DATETIME,
	"page_id"	INTEGER,
	PRIMARY KEY("id"),
	UNIQUE("message_id"),
	FOREIGN KEY("page_id") REFERENCES "facebook_page"("id")
);
INSERT INTO "auto_response" VALUES (1,'bonjour, salut, hello, hi','Bonjour ! 👋 Merci de nous contacter. Comment puis-je vous aider aujourd''hui ?','both',1,50,'2025-11-22 08:46:45.468358');
INSERT INTO "auto_response" VALUES (2,'prix, coût, tarif, combien','Nos prix varient selon les produits. Pour un devis personnalisé, contactez-nous directement ou consultez notre catalogue.','both',1,80,'2025-11-22 08:46:45.474031');
INSERT INTO "auto_response" VALUES (3,'disponible, dispo, stock, reste','Nous vérifions nos stocks en temps réel. La plupart de nos produits sont disponibles immédiatement.','both',1,70,'2025-11-22 08:46:45.475536');
INSERT INTO "auto_response" VALUES (4,'livraison, délai, expédition, envoyer','Nous livrons sous 2-3 jours ouvrés. Les frais de port sont calculés selon votre localisation.','both',1,75,'2025-11-22 08:46:45.476648');
INSERT INTO "auto_response" VALUES (5,'commander, acheter, prendre, réserver','Super ! Pour passer commande, envoyez-nous un message privé avec les détails de ce que vous souhaitez.','both',1,90,'2025-11-22 08:46:45.477902');
INSERT INTO "auto_response" VALUES (6,'contact, téléphone, email, appeler','Vous pouvez nous joindre par message privé ici, ou appelez-nous au +261 XX XXX XX XX.','both',1,85,'2025-11-22 08:46:45.479897');
INSERT INTO "auto_response" VALUES (7,'problème, souci, erreur, aide','Nous sommes désolés pour ce désagrément. Pouvez-vous nous donner plus de détails ? Notre équipe va vous aider rapidement.','both',1,95,'2025-11-22 08:46:45.481683');
INSERT INTO "auto_response" VALUES (8,'merci, thanks, remercie','Avec plaisir ! 😊 N''hésitez pas si vous avez d''autres questions.','both',1,40,'2025-11-22 08:46:45.482921');
INSERT INTO "auto_response" VALUES (9,'horaire, ouvert, fermé, heure','Nous sommes ouverts du Lundi au Vendredi de 9h à 17h, Samedi de 9h à 13h. Fermé le Dimanche.','both',1,60,'2025-11-22 08:46:45.484156');
INSERT INTO "auto_response" VALUES (10,'info, information, renseignement, détail','Bien sûr ! De quoi avez-vous besoin exactement ? Je suis là pour vous renseigner.','both',1,50,'2025-11-22 08:46:45.485170');
INSERT INTO "comment" VALUES (1,'sample_comment_1763776073.46389','post_6034','user_100','Alice Petit','Super produit ! Je recommande','Merci beaucoup pour votre retour positif ! 😊',1,'2025-11-22 04:47:53.463890',1);
INSERT INTO "comment" VALUES (2,'sample_comment_1763779673.464309','post_6847','user_101','Bob Grand','C''est combien ?','Nos prix varient selon les produits. Contactez-nous en message privé pour plus d''infos.',1,'2025-11-22 05:47:53.464309',1);
INSERT INTO "comment" VALUES (3,'sample_comment_1763783273.465279','post_3987','user_102','Claire Moyen','Encore disponible ?','Oui, nous avons du stock disponible !',1,'2025-11-22 06:47:53.465279',1);
INSERT INTO "comment" VALUES (4,'sample_comment_1763786873.465809','post_1343','user_103','David Long','Comment commander ?','Envoyez-nous un message privé avec ce que vous souhaitez commander.',1,'2025-11-22 07:47:53.465809',1);
INSERT INTO "comment" VALUES (5,'sample_comment_1763778922.29059','post_6510','user_100','Alice Petit','Super produit ! Je recommande','Merci beaucoup pour votre retour positif ! 😊',1,'2025-11-22 05:35:22.290590',1);
INSERT INTO "comment" VALUES (6,'sample_comment_1763782522.290895','post_8127','user_101','Bob Grand','C''est combien ?','Nos prix varient selon les produits. Contactez-nous en message privé pour plus d''infos.',1,'2025-11-22 06:35:22.290895',1);
INSERT INTO "comment" VALUES (7,'sample_comment_1763786122.291242','post_6952','user_102','Claire Moyen','Encore disponible ?','Oui, nous avons du stock disponible !',1,'2025-11-22 07:35:22.291242',1);
INSERT INTO "comment" VALUES (8,'sample_comment_1763789722.291612','post_5039','user_103','David Long','Comment commander ?','Envoyez-nous un message privé avec ce que vous souhaitez commander.',1,'2025-11-22 08:35:22.291612',1);
INSERT INTO "comment" VALUES (9,'sample_comment_1763778925.451231','post_7733','user_100','Alice Petit','Super produit ! Je recommande','Merci beaucoup pour votre retour positif ! 😊',1,'2025-11-22 05:35:25.451231',1);
INSERT INTO "comment" VALUES (10,'sample_comment_1763782525.451869','post_9916','user_101','Bob Grand','C''est combien ?','Nos prix varient selon les produits. Contactez-nous en message privé pour plus d''infos.',1,'2025-11-22 06:35:25.451869',1);
INSERT INTO "comment" VALUES (11,'sample_comment_1763786125.45277','post_2774','user_102','Claire Moyen','Encore disponible ?','Oui, nous avons du stock disponible !',1,'2025-11-22 07:35:25.452770',1);
INSERT INTO "comment" VALUES (12,'sample_comment_1763789725.453711','post_2828','user_103','David Long','Comment commander ?','Envoyez-nous un message privé avec ce que vous souhaitez commander.',1,'2025-11-22 08:35:25.453711',1);
INSERT INTO "facebook_page" VALUES (1,'test_page_123','Page de Test','test_token_replace_with_real_token',1,'2025-11-22 08:47:36.226498');
INSERT INTO "message" VALUES (1,'sample_msg_1763772472.947187','user_1','Jean Dupont','Bonjour, je voudrais des informations sur vos produits','Bonjour ! 👋 Merci de nous contacter. Comment puis-je vous aider aujourd''hui ?',1,'2025-11-22 03:47:52.947187',1);
INSERT INTO "message" VALUES (2,'sample_msg_1763776072.973673','user_2','Marie Martin','Quel est le prix de ce produit ?','Nos prix varient selon les produits. Pour un devis personnalisé, contactez-nous directement.',1,'2025-11-22 04:47:52.973673',1);
INSERT INTO "message" VALUES (3,'sample_msg_1763779672.994301','user_3','Pierre Durand','Est-ce disponible en stock ?','Nous vérifions nos stocks en temps réel. La plupart de nos produits sont disponibles immédiatement.',1,'2025-11-22 05:47:52.994301',1);
INSERT INTO "message" VALUES (4,'sample_msg_1763783272.995265','user_4','Sophie Bernard','Je voudrais commander ce produit','Super ! Pour passer commande, envoyez-nous un message privé avec les détails.',1,'2025-11-22 06:47:52.995265',1);
INSERT INTO "message" VALUES (5,'sample_msg_1763786872.995545','user_5','Luc Robert','Merci beaucoup pour votre aide !','Avec plaisir ! 😊 N''hésitez pas si vous avez d''autres questions.',1,'2025-11-22 07:47:52.995545',1);
INSERT INTO "message" VALUES (6,'sample_msg_1763775319.751841','user_1','Jean Dupont','Bonjour, je voudrais des informations sur vos produits','Bonjour ! 👋 Merci de nous contacter. Comment puis-je vous aider aujourd''hui ?',1,'2025-11-22 04:35:19.751841',1);
INSERT INTO "message" VALUES (7,'sample_msg_1763778919.752141','user_2','Marie Martin','Quel est le prix de ce produit ?','Nos prix varient selon les produits. Pour un devis personnalisé, contactez-nous directement.',1,'2025-11-22 05:35:19.752141',1);
INSERT INTO "message" VALUES (8,'sample_msg_1763782519.752612','user_3','Pierre Durand','Est-ce disponible en stock ?','Nous vérifions nos stocks en temps réel. La plupart de nos produits sont disponibles immédiatement.',1,'2025-11-22 06:35:19.752612',1);
INSERT INTO "message" VALUES (9,'sample_msg_1763786119.753247','user_4','Sophie Bernard','Je voudrais commander ce produit','Super ! Pour passer commande, envoyez-nous un message privé avec les détails.',1,'2025-11-22 07:35:19.753247',1);
INSERT INTO "message" VALUES (10,'sample_msg_1763789719.754171','user_5','Luc Robert','Merci beaucoup pour votre aide !','Avec plaisir ! 😊 N''hésitez pas si vous avez d''autres questions.',1,'2025-11-22 08:35:19.754171',1);
INSERT INTO "message" VALUES (11,'sample_msg_1763775325.274745','user_1','Jean Dupont','Bonjour, je voudrais des informations sur vos produits','Bonjour ! 👋 Merci de nous contacter. Comment puis-je vous aider aujourd''hui ?',1,'2025-11-22 04:35:25.274745',1);
INSERT INTO "message" VALUES (12,'sample_msg_1763778925.275053','user_2','Marie Martin','Quel est le prix de ce produit ?','Nos prix varient selon les produits. Pour un devis personnalisé, contactez-nous directement.',1,'2025-11-22 05:35:25.275053',1);
INSERT INTO "message" VALUES (13,'sample_msg_1763782525.275328','user_3','Pierre Durand','Est-ce disponible en stock ?','Nous vérifions nos stocks en temps réel. La plupart de nos produits sont disponibles immédiatement.',1,'2025-11-22 06:35:25.275328',1);
INSERT INTO "message" VALUES (14,'sample_msg_1763786125.27561','user_4','Sophie Bernard','Je voudrais commander ce produit','Super ! Pour passer commande, envoyez-nous un message privé avec les détails.',1,'2025-11-22 07:35:25.275610',1);
INSERT INTO "message" VALUES (15,'sample_msg_1763789725.27582','user_5','Luc Robert','Merci beaucoup pour votre aide !','Avec plaisir ! 😊 N''hésitez pas si vous avez d''autres questions.',1,'2025-11-22 08:35:25.275820',1);
COMMIT;

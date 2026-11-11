# SIMC PBX

Infraestructura de telefonía VoIP modular y escalable basada en contenedores Docker, orientada al procesamiento en tiempo real, enrutamiento dinámico y servicios de transcripción automática (STT).

---

## Arquitectura del Sistema

El entorno se despliega sobre una red puente privada (`pbx_network`) que interconecta los siguientes componentes:

*   **Asterisk PBX:** Servidor SIP y motor de conmutación de llamadas gestionado con el canal `pjsip`. Soporta señalización TCP/UDP en el puerto `5060` y rangos RTP para medios.
*   **Go Security & Routing Middleware `go_security`:** Servicio de alto rendimiento desarrollado en Go con arquitectura *worker pool*. Implementa un demonio FastAGI en el puerto `4573` para el control de llamadas y un endpoint HTTP en el puerto `8080` para monitoreo de salud.
*   **Redis Cache & Datastore `redis_service`:** Base de datos en memoria para el almacenamiento de rutas dinámicas, variables de contexto y estados de extensiones sin requerir recargas en el dialplan.
*   **Servicio STT `stt_service`:** Microservicio para transcripción de audio e inferencia de voz a texto a través de peticiones HTTP REST.

---

## Requisitos Previos

*   Sistema Operativo: Linux Debian Based (probado en Linux Mint / Ubuntu LTS).
*   Docker Engine versión 24.0 o superior.
*   Docker Compose v2.
*   Cliente SIP para pruebas (Linphone o Zoiper) funciona mejor en Zoiper.

---
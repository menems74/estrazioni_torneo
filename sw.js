/* Il guardiano che tiene la pagina in tasca.

   Serve a due cose: far comparire "Installa App" sui telefoni Android, e
   far funzionare il sorteggio anche senza linea, che al bar capita.
   Per le pagine prova prima la rete, cosi' chi e' online vede subito la
   versione nuova; per il resto (icone, manifesto) pesca dalla dispensa. */

var DISPENSA = 'estrazione-torneo-v1';
var ROBA = [
  './',
  './index.html',
  './favicon.svg',
  './manifest.webmanifest',
  './icona-192.png',
  './icona-512.png'
];

self.addEventListener('install', function(e){
  e.waitUntil(caches.open(DISPENSA).then(function(c){ return c.addAll(ROBA); }));
  self.skipWaiting();
});

self.addEventListener('activate', function(e){
  e.waitUntil(
    caches.keys().then(function(nomi){
      return Promise.all(nomi.map(function(n){
        return n === DISPENSA ? null : caches.delete(n);
      }));
    }).then(function(){ return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function(e){
  var r = e.request;
  if(r.method !== 'GET') return;

  if(r.mode === 'navigate'){
    e.respondWith(
      fetch(r).then(function(risposta){
        var copia = risposta.clone();
        caches.open(DISPENSA).then(function(c){ c.put('./index.html', copia); });
        return risposta;
      }).catch(function(){
        return caches.match('./index.html');
      })
    );
    return;
  }

  e.respondWith(
    caches.match(r).then(function(trovato){
      return trovato || fetch(r).then(function(risposta){
        if(risposta.ok && new URL(r.url).origin === location.origin){
          var copia = risposta.clone();
          caches.open(DISPENSA).then(function(c){ c.put(r, copia); });
        }
        return risposta;
      });
    })
  );
});

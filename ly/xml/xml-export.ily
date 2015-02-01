\version "2.18.2"


%%% code to map music data to XML

%{

\relative {
  c d e
}

maps to (scheme):

(make-music
  'RelativeOctaveMusic
  'element
  (make-music
    'SequentialMusic
    'elements
    (list (make-music
            'NoteEvent
            'pitch
            (ly:make-pitch -1 0 0)
            'duration
            (ly:make-duration 2 0 1))
          (make-music
            'NoteEvent
            'pitch
            (ly:make-pitch -1 1 0)
            'duration
            (ly:make-duration 2 0 1))
          (make-music
            'NoteEvent
            'pitch
            (ly:make-pitch -1 2 0)
            'duration
            (ly:make-duration 2 0 1)))))

maps to xml:

<music name="RelativeOctaveMusic">
  <element>
    <music name="SequentialMusic">
      <elements>
        <music name="NoteEvent">
          <pitch octave="-1" step="0" alter="0"/>
          <duration log="2" dots="0" num="1" den="1"/>
        </music>
        <music name="NoteEvent">
          <pitch octave="-1" step="1" alter="0"/>
          <duration log="2" dots="0" num="1" den="1"/>
        </music>
        <music name="NoteEvent">
          <pitch octave="-1" step="2" alter="0"/>
          <duration log="2" dots="0" num="1" den="1"/>
        </music>
      </elements>
    </music>
  </element>
</music>

We can also access the origin of each music object:

<music name="NoteEvent>
  <origin file="/bla.ly" line="1" char="3" column="4"/>


%}

#(define indent-width 2)

% convert a name value pair to an xml attribute
#(define (attr->string name value)
   (string-append name "=\"" value "\""))


% convert an assoc list to an xml attribute string (joined with a space in between)
#(define (attrs->string attrs)
   (string-join
     (map (lambda (e)
            (attr->string (car e) (cdr e))) attrs)
     " " 'prefix))
  
% escape string for xml attribute
#(define (attribute-escape s)
   (ly:string-substitute "\"" "&quot;" (ly:string-substitute "&" "&amp;" s)))

% escape string for xml body
#(define (xml-escape s)
   (ly:string-substitute "<" "&lt;" 
     (ly:string-substitute ">" "&gt;" 
       (ly:string-substitute "\"" "&quot;" 
         (ly:string-substitute "&" "&amp;" s)))))


% show an open or close tag (for close, prefix the name with a "/")
#(define (tag name indent)
   (atag name indent '()))

% show a tag with attributes
#(define (atag name indent attrs)
   (let ((s (string-append
             (make-string (* indent-width indent) #\space)
             "<" name (attrs->string attrs) ">\n")))
     (display s)))

% show a open-close tag with attributes
#(define (atagc name indent attrs)
   (let ((s (string-append
             (make-string (* indent-width indent) #\space)
             "<" name (attrs->string attrs) "/>\n")))
     (display s)))



% convert any object to XML
% currently the xml is just (display)ed but later it will be written to a file or string.
% the object is always returned
#(define (obj->lily-xml o indent)
   (cond
    ((ly:music? o)
      (let ((name (ly:music-property o 'name))
            (e (ly:music-property o 'element))
            (es (ly:music-property o 'elements))
            (as (ly:music-property o 'articulations))
            (tw (ly:music-property o 'tweaks))
            (location (ly:music-property o 'origin))
            )
        (atag "music" indent (acons "name" (symbol->string name) '()))
        (if (ly:music? e)
            (begin 
              (tag "element" (+ indent 1))
              (obj->lily-xml e (+ indent 2))
              (tag "/element" (+ indent 1))))
        (if (and (list? es) (not (null? es)))
            (begin 
              (tag "elements" (+ indent 1))
              (for-each (lambda (e)
                          (obj->lily-xml e (+ indent 2))) es)
              (tag "/elements" (+ indent 1))))
        (if (and (list? as) (not (null? as)))
            (begin 
              (tag "articulations" (+ indent 1))
              (for-each (lambda (e)
                          (obj->lily-xml e (+ indent 2))) as)
              (tag "/articulations" (+ indent 1))))
        (if (and (list? tw) (not (null? tw)))
            (begin 
              (tag "tweaks" (+ indent 1))
              (for-each (lambda (e)
                          (obj->lily-xml e (+ indent 2))) tw)
              (tag "/tweaks" (+ indent 1))))
        (if (ly:input-location? location)
            (let ((origin (ly:input-file-line-char-column location)))
              (atagc "origin" (+ indent 1) (list
                 `("filename" . ,(attribute-escape (car origin)))
                 `("line"     . ,(number->string (cadr origin)))
                 `("char"     . ,(number->string (caddr origin)))))))
        (tag "/music" indent)))
    
    ((number? o)
     (atagc "number" indent (acons "value" (number->string o) '())))
    ((string? o)
     (atagc "string" indent (acons "value" (attribute-escape o) '())))
    ((boolean? o)
     (atagc "boolean" indent (acons "value" (if o "true" "false") '())))
    ((symbol? o)
     (atagc "symbol" indent (acons "value" (symbol->string o) '())))
    ((list? o)
     (if (null? o)
         (atagc "null" indent '()) ; or <list/> ??
         (begin
          (tag "list" indent)
          (for-each (lambda (e)
                 (obj->lily-xml e (+ indent 1))) o)
          (tag "/list" indent))))
    ((pair? o)
     (begin
       (tag "pair" indent)
       (obj->lily-xml (car o) (+ indent 1))
       (obj->lily-xml (cdr o) (+ indent 1))
       (tag "/pair" indent)))
      
    )
  
  
  o)

displayLilyXML = #
(define-music-function (parser location music) (ly:music?)
  (obj->lily-xml music 0))

% \displayLilyXML { c d-\tweak color red -. e }

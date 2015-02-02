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

% convert an assoc list to an xml attribute string (joined with a space in between)
#(define (attrs->string attrs)
   (string-join
     (map (lambda (e)
            (attr->string (car e) (cdr e))) attrs)
     " " 'prefix))
  
% convert a name value pair to an xml attribute
% name is a symbol, value can be a symbol, string, or number
#(define (attr->string name value)
   (string-append (symbol->string name)
     "=\""
     (cond 
      ((string? value) (attribute-escape value))
      ((number? value) (number->string value))
      ((symbol? value) (symbol->string value)))
     "\""))

% escape string for xml body
#(define (xml-escape s)
   (ly:string-substitute "<" "&lt;" 
     (ly:string-substitute ">" "&gt;" 
       (attribute-escape s))))

% escape string for xml attribute
#(define (attribute-escape s)
   (ly:string-substitute "\"" "&quot;"
     (ly:string-substitute "&" "&amp;" s)))


% show a tag
#(define (xml-tag name indent attrs close-tag)
   (let ((s (string-append
             (make-string (* indent-width indent) #\space)
             "<"
             (if (eq? close-tag 'close) "/" "")
             (symbol->string name)
             (attrs->string attrs)
             (if (eq? close-tag 'self-close) "/" "")
             ">\n")))
     (display s)))
   
% show an open tag
#(define (open-tag name indent attrs)
   (xml-tag name indent attrs #f))

% show a close tag
#(define (close-tag name indent)
   (xml-tag name indent '() 'close))

% show a self-closing tag
#(define (self-close-tag name indent attrs)
   (xml-tag name indent attrs 'self-close))



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
            (pitch (ly:music-property o 'pitch))
            (duration (ly:music-property o 'duration))
            )
        (open-tag 'music indent (acons 'name name '()))
        (if (ly:input-location? location)
            (let ((origin (ly:input-file-line-char-column location)))
              (self-close-tag 'origin (+ indent 1)
                `((filename . ,(car origin))
                  (line     . ,(cadr origin))
                  (char     . ,(caddr origin))))))
        (if (ly:pitch? pitch)
            (self-close-tag 'pitch (+ indent 1)
              `((octave . ,(ly:pitch-octave pitch))
                (notename . ,(ly:pitch-notename pitch))
                (alteration . ,(ly:pitch-alteration pitch)))))
        (if (ly:duration? duration)
            (self-close-tag 'duration (+ indent 1)
              `((log . ,(ly:duration-log duration))
                   (dots . ,(ly:duration-dot-count duration))
                   (numer . ,(car (ly:duration-factor duration)))
                   (denom . ,(cdr (ly:duration-factor duration))))))
        (if (ly:music? e)
            (begin 
              (open-tag 'element (+ indent 1) '())
              (obj->lily-xml e (+ indent 2))
              (close-tag 'element (+ indent 1))))
        (if (and (list? es) (not (null? es)))
            (begin 
              (open-tag 'elements (+ indent 1) '())
              (for-each (lambda (e)
                          (obj->lily-xml e (+ indent 2))) es)
              (close-tag 'elements (+ indent 1))))
        (if (and (list? as) (not (null? as)))
            (begin 
              (open-tag 'articulations (+ indent 1) '())
              (for-each (lambda (e)
                          (obj->lily-xml e (+ indent 2))) as)
              (close-tag 'articulations (+ indent 1))))
        (if (and (list? tw) (not (null? tw)))
            (begin 
              (open-tag 'tweaks (+ indent 1) '())
              (for-each (lambda (e)
                          (obj->lily-xml e (+ indent 2))) tw)
              (close-tag 'tweaks (+ indent 1))))
        (close-tag 'music indent)))
    
    ((number? o)
     (self-close-tag 'number indent `((value . ,o))))
    ((string? o)
     (self-close-tag 'string indent `((value  . ,o))))
    ((char? o)
     (self-close-tag 'char indent `((value . ,(string o)))))
    ((boolean? o)
     (self-close-tag 'boolean indent `((value . ,(if o 'true 'false)))))
    ((symbol? o)
     (self-close-tag 'symbol indent `((value . ,o))))
    ((null? o)
     (self-close-tag 'null indent '())) ; or <list/> ??
    ((list? o)
     (begin
       (open-tag 'list indent '())
       (for-each (lambda (e)
                   (obj->lily-xml e (+ indent 1))) o)
       (close-tag 'list indent)))
    ((pair? o)
     (begin
       (open-tag 'pair indent '())
       (obj->lily-xml (car o) (+ indent 1))
       (obj->lily-xml (cdr o) (+ indent 1))
       (close-tag 'pair indent)))
      
    )
  
  
  o)

displayLilyXML = #
(define-music-function (parser location music) (ly:music?)
  (obj->lily-xml music 0))

% \displayLilyXML { c d-\tweak color #red -. e }

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

% convert a name value pair to an xml attribute
#(define (attr->string name value)
   (string-append name "=\"" value "\""))


% convert an assoc list to an xml attribute string (joined with a space in between)
#(define (attrs->string attrs)
   (string-join
     (map (lambda (e)
            (attr->string (car e) (cdr e))) attrs)
     " " 'prefix))
  

% show an open or close tag (for close, prefix the name with a "/")
#(define (tag name indent)
   (let ((s (string-append
             (make-string indent #\space)
             "<" name ">\n")))
     (display s)))

% show a tag with attributes
#(define (atag name indent attrs)
   (let ((s (string-append
             (make-string indent #\space)
             "<" name (attrs->string attrs) ">\n")))
     (display s)))



#
(define (music->lily-xml m indent)
  (let ((name (ly:music-property m 'name))
        (e (ly:music-property m 'element))
        (es (ly:music-property m 'elements))
        (as (ly:music-property m 'articulations))
        (tw (ly:music-property m 'tweaks))
        )
    (atag "music" indent (acons "name" (symbol->string name) '()))
    (if (ly:music? e)
        (begin 
          (tag "element" (+ indent 2))
          (music->lily-xml e (+ indent 4))
          (tag "/element" (+ indent 2))))
    (if (and (list? es) (not (null? es)))
        (begin 
          (tag "elements" (+ indent 2))
          (for-each (lambda (e)
                      (music->lily-xml e (+ indent 4))) es)
          (tag "/elements" (+ indent 2))))
    (if (and (list? as) (not (null? as)))
        (begin 
          (tag "articulations" (+ indent 2))
          (for-each (lambda (e)
                      (music->lily-xml e (+ indent 4))) as)
          (tag "/articulations" (+ indent 2))))
    (if (and (list? tw) (not (null? tw)))
        (begin 
          (tag "tweaks" (+ indent 2))
          (for-each (lambda (e)
                      (music->lily-xml e (+ indent 4))) tw)
          (tag "/tweaks" (+ indent 2))))
    
    )
  
    (tag "/music" indent)
  
  m)

displayLilyXML = #
(define-music-function (parser location music) (ly:music?)
  (music->lily-xml music 0))


% \displayLilyXML { c d-. e }

